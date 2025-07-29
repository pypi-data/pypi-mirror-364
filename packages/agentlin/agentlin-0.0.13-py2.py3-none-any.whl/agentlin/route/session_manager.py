from collections import defaultdict
from pathlib import Path
from typing_extensions import Any, AsyncGenerator, AsyncIterable, TypedDict
import json
import traceback
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from fastmcp import Client as MCPClient
from sse_starlette.sse import EventSourceResponse
from pydantic import ValidationError
from loguru import logger

from xlin import load_json
from deeplin.inference_engine import build_inference_engine
from agentlin.code_interpreter.types import Block
from agentlin.core.types import *
from agentlin.core.agent_schema import AgentCore, extract_code, extract_thought, parse_function_call_response, remove_thoughts
from agentlin.route.task_manager import TaskManager, InMemoryTaskManager, merge_streams
from agentlin.route.tool_task_manager import ToolTaskManager
from agentlin.route.code_task_manager import CodeTaskManager, ExecuteRequest
from agentlin.route.agent_task_manager import AgentTaskManager


class CodeInterpreterConfig(BaseModel):
    jupyter_host: str  # Jupyter host URL
    jupyter_port: int  # Jupyter port
    jupyter_token: str  # Jupyter token
    jupyter_timeout: int  # Jupyter timeout
    jupyter_username: str  # Jupyter username


class AgentConfig(BaseModel):
    id: str
    name: str
    description: str
    version: str
    engine: str
    model: str
    code_for_agent: str
    code_for_interpreter: str
    tool_mcp_config: dict[str, Any] = {
        "mcpServers": {
            "aime_sse_server": {"url": "http://localhost:7778/tool_mcp"},
        }
    }
    code_mcp_config: dict[str, Any] = {
        "mcpServers": {
            "aime_sse_server": {"url": "http://localhost:7778/code_mcp"},
        }
    }
    a2a_config: dict[str, Any] = {}
    code_interpreter_config: CodeInterpreterConfig
    inference_args: dict[str, Any] = {}


class SessionState(BaseModel):
    session_id: str
    user_id: str
    host_frontend_id: str
    host_agent_id: str
    host_code_kernel_id: Optional[str] = None
    agent_config: AgentConfig

    # 短期记忆
    history_messages: list[DialogData] = []
    thought_messages: list[DialogData] = []
    execution_messages: list[DialogData] = []
    block_list: list[Block] = []
    citation_block_dict: dict[int, Block] = {}  # citation id to block

    # 运行时 - 这些属性不参与 BaseModel 的序列化和验证
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}

    def __init__(self, **data):
        # 提取运行时管理器，避免传入 BaseModel 验证
        agent_task_manager = data.pop('agent_task_manager', None)
        tool_task_manager = data.pop('tool_task_manager', None)
        code_task_manager = data.pop('code_task_manager', None)

        # 先调用父类的 __init__
        super().__init__(**data)

        # 然后设置运行时属性
        self.agent_task_manager: AgentTaskManager = agent_task_manager
        self.tool_task_manager: ToolTaskManager = tool_task_manager
        self.code_task_manager: CodeTaskManager = code_task_manager


async def get_agent_id(host_frontend_id: str) -> str:
    return "aime"

def parse_config_from_ipynb(ipynb_path: str):
    json_data = load_json(ipynb_path)
    cells = json_data["cells"]
    code_for_interpreter = "".join(cells[1]["source"])  # 第二个cell的内容
    code_for_agent = "".join(cells[3]["source"])  # 第四个cell的内容
    return code_for_interpreter, code_for_agent

async def get_agent_config(agent_id: str) -> AgentConfig:
    # 这里可以根据 agent_id 从数据库或配置文件中获取 AgentConfig
    # 这里使用一个示例配置
    path = Path(__file__).parent / "example.ipynb"
    code_for_interpreter, code_for_agent = parse_config_from_ipynb(path)
    json_data = {
        "id": "aime",
        "name": "AIME Agent",
        "description": "AIME Agent for handling user requests",
        "version": "1.0.0",
        "engine": "api",
        "model": "o3",
        "code_for_interpreter": code_for_interpreter,
        "code_for_agent": code_for_agent,
        "a2a_config": {},
        "tool_mcp_config": {
            "mcpServers": {
                "aime_sse_server": {"url": "http://localhost:7778/tool_mcp"},
            }
        },
        "code_mcp_config": {
            "mcpServers": {
                "aime_sse_server": {"url": "http://localhost:7778/code_mcp"},
            }
        },
        "code_interpreter_config": {
            "jupyter_host": "localhost",
            "jupyter_port": 8888,
            "jupyter_token": "jupyter_server_token",
            "jupyter_timeout": 60,
            "jupyter_username": "user",
        },
    }
    config = AgentConfig.model_validate(json_data)
    return config


class SessionTaskManager(InMemoryTaskManager):
    def __init__(self, callback_url: str):
        super().__init__()
        self.sessions: dict[str, SessionState] = {}
        self.callback_url = callback_url

    async def build_agent_task_manager(self, session_id: str, agent_config: AgentConfig) -> AgentTaskManager:
        engine = agent_config.engine
        model = agent_config.model
        engine = build_inference_engine(engine, model)
        agent_core = AgentCore(
            engine=engine,
        )
        return AgentTaskManager(agent_core)

    async def build_tool_task_manager(self, session_id: str, agent_config: AgentConfig) -> ToolTaskManager:
        tool_mcp_config = agent_config.tool_mcp_config
        tool_mcp_client = MCPClient(tool_mcp_config)
        # async with tool_mcp_client:
        #     tools = await tool_mcp_client.list_tools()
        tool_task_manager = ToolTaskManager(
            config=tool_mcp_config,
            callback_url=self.callback_url,
        )
        return tool_task_manager

    async def build_code_task_manager(self, session_id: str, agent_config: AgentConfig) -> CodeTaskManager:
        code_interpreter_config = agent_config.code_interpreter_config
        if not code_interpreter_config:
            raise ValueError("Code interpreter configuration is required for CodeTaskManager.")
        return CodeTaskManager(
            jupyter_host=code_interpreter_config.jupyter_host,
            jupyter_port=code_interpreter_config.jupyter_port,
            jupyter_token=code_interpreter_config.jupyter_token,
            jupyter_timeout=code_interpreter_config.jupyter_timeout,
            jupyter_username=code_interpreter_config.jupyter_username,
        )

    def build_system_code(self, session_id: str, session_state: SessionState) -> str:
        code_mcp_config = session_state.agent_config.code_mcp_config
        code_for_interpreter = session_state.agent_config.code_for_interpreter
        code_for_agent = session_state.agent_config.code_for_agent

        total_code = code_for_interpreter.replace("{code_mcp_config}", json.dumps(code_mcp_config, ensure_ascii=False))
        # total_code = total_code + code_for_agent
        return total_code

    async def lazy_init_kernel(self, session_id: str, session_state: SessionState) -> str:
        kernel_id = session_state.host_code_kernel_id
        if kernel_id:
            return kernel_id
        code_task_manager = session_state.code_task_manager
        kernel_id = code_task_manager.create_kernel()
        session_state.host_code_kernel_id = kernel_id
        system_code = self.build_system_code(session_id, session_state)
        req = ExecuteRequest(
            kernel_id=kernel_id,
            code=system_code,
            mode="full",
        )
        request = SendTaskRequest(
            params=TaskSendParams(
                sessionId=session_id,
                payload=req.model_dump(),
            )
        )
        await code_task_manager.on_send_task(request)
        return kernel_id

    # async def elicitation_handler(self, message: str, response_type: type, params: ElicitRequestParams, context: Context):
    #     # Present the message to the user and collect input
    #     # user_input = input(f"{message}: ")
    #     print(f"{message}")
    #     print("===Params===")
    #     print(params)
    #     print("===Context===")
    #     print(context)
    #     data = {
    #         "callback_url": self.callback_url,
    #         "params": params.model_dump(),
    #     }
    #     # display_event(Event(type="elicitation", data=data))

    #     return ElicitResult(action="accept")

    async def create_session(self, session_id: str, user_id: str, host_frontend_id: str) -> SessionState:
        if session_id in self.sessions and self.sessions[session_id]:
            logger.warning(f"Session {session_id} already exists.")
            return self.sessions[session_id]
        host_agent_id = await get_agent_id(host_frontend_id)
        host_agent_config = await get_agent_config(host_agent_id)
        host_agent_id = host_agent_config.id

        agent_task_manager = await self.build_agent_task_manager(session_id, host_agent_config)
        tool_task_manager = await self.build_tool_task_manager(session_id, host_agent_config)
        code_task_manager = await self.build_code_task_manager(session_id, host_agent_config)

        state = SessionState(
            session_id=session_id,
            user_id=user_id,
            host_frontend_id=host_frontend_id,
            host_agent_id=host_agent_id,
            host_code_kernel_id=None,
            agent_config=host_agent_config,
            tool_task_manager=tool_task_manager,
            code_task_manager=code_task_manager,
            agent_task_manager=agent_task_manager,
        )
        self.sessions[session_id] = state
        return state

    def get_session(self, session_id: str):
        return self.sessions.get(session_id, None)

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            session_state = self.sessions[session_id]
            kernel_id = session_state.host_code_kernel_id
            if kernel_id:
                session_state.code_task_manager.delete_kernel(kernel_id)
            del self.sessions[session_id]

    async def _stream_generator(self, request: SendTaskStreamingRequest) -> AsyncGenerator[SendTaskStreamingResponse | JSONRPCResponse, Any]:
        task_send_params: TaskSendParams = request.params
        payload = task_send_params.payload
        session_id = task_send_params.sessionId
        user_id = payload["userId"]
        host_frontend_id = payload["hostFrontendId"]
        user_message_content = payload["user_message_content"]
        msg_key = payload.get("msg_key", f"msg_{uuid.uuid4().hex}")
        session_state = self.get_session(session_id)
        if session_state is None:
            session_state = await self.create_session(session_id, user_id, host_frontend_id)
        agent_task_manager = session_state.agent_task_manager
        tool_task_manager = session_state.tool_task_manager
        code_task_manager = session_state.code_task_manager
        history_messages: list[dict] = session_state.history_messages
        thought_messages: list[dict] = session_state.thought_messages
        inference_args: dict = session_state.agent_config.inference_args
        debug = inference_args.get("debug", False)
        current_step = 0
        if len(thought_messages) > 0:
            current_step = sum([1 for m in thought_messages if m["role"] == "assistant"])

        task_status = TaskStatus(state=TaskState.WORKING)
        await self.update_store(task_send_params.id, task_status)
        yield SendTaskStreamingResponse(
            id=request.id,
            result=TaskStatusUpdateEvent(
                id=task_send_params.id,
                status=task_status,
                final=False,
            ),
        )

        history_messages.append({"role": "user", "content": user_message_content})

        while True:
            current_step += 1
            if debug:
                logger.debug(f"当前推理深度: {current_step}, 历史消息数量: {len(history_messages)}")
            # 调用推理引擎获取回复
            messages = history_messages + thought_messages
            print(messages)

            reasoning_content = []
            response = agent_task_manager.agent.engine.inference_one(messages, **inference_args)
            if debug:
                logger.debug(f"🤖【assistant】: {response}")

            # "tool_calls": [
            #     {
            #         "function": {
            #             "arguments": "{}",
            #             "name": "Search"
            #         },
            #         "id": "call_g16uvNKM2r7L36PcHmgbPAAo",
            #         "type": "function"
            #     }
            # ]
            tool_calls: list[dict] = []
            if isinstance(response, dict):
                # TODO 把 reasoning 给前端
                tool_calls.append(response)
            elif isinstance(response, list):
                # TODO 把 reasoning 给前端
                tool_calls.extend(response)
            else:
                thought = extract_thought(response)
                if thought:
                    reasoning_content.append({"type": "text", "text": [{"type": "text", "text": "<think>"}]})
                    reasoning_content.append({"type": "text", "text": thought})
                    reasoning_content.append({"type": "text", "text": [{"type": "text", "text": "</think>"}]})

                response_without_thoughts = remove_thoughts(response)
                code = extract_code(response_without_thoughts)
                call_id = f"call_{uuid.uuid4().hex}"
                if code and len(code.strip()) > 0:
                    call_args = {
                        "code": code,
                    }
                    tool_call = {
                        "function": {
                            "arguments": json.dumps(call_args, ensure_ascii=False),
                            "name": "CodeInterpreter",
                        },
                        "id": call_id,
                        "type": "function",
                    }
                    tool_calls.append(tool_call)

            if reasoning_content:
                yield SendTaskStreamingResponse(
                    id=request.id,
                    result=TaskArtifactUpdateEvent(
                        id=task_send_params.id,
                        metadata={
                            "block_list": reasoning_content,
                            "msg_key": msg_key,
                            "current_step": current_step,
                            "key": f"{msg_key}_assistant_thought_{current_step}",
                        },
                    ),
                )
                thought_messages.append({"role": "assistant", "content": reasoning_content})

            if tool_calls:
                # 1. 开始执行
                id_name_args_list: list[tuple[str, str, dict[str, Any]]] = []
                block_list = []
                for tool_call in tool_calls:
                    call_id, call_name, call_args = parse_function_call_response(tool_call)
                    id_name_args_list.append((call_id, call_name, call_args))
                    block_list.append(
                        {
                            "type": "tool_call",
                            "status": "executing",
                            "call_id": call_id,
                            "call_name": call_name,
                            "call_args": call_args,
                        }
                    )
                yield SendTaskStreamingResponse(
                    id=request.id,
                    result=TaskArtifactUpdateEvent(
                        id=task_send_params.id,
                        metadata={
                            "block_list": block_list,
                            "msg_key": msg_key,
                            "current_step": current_step,
                            "key": f"{msg_key}_assistant_msg_{current_step}",
                        },
                    ),
                )
                # 2. 记录工具调用到上下文
                thought_messages.append({"role": "assistant", "content": "", "tool_calls": tool_calls})

                # 3. 执行
                call_response_streams = []
                call_id_for_code_interpreter = None
                for call_id, call_name, call_args in id_name_args_list:
                    if call_name == "CodeInterpreter":
                        code = call_args.get("code", "")
                        call_id_for_code_interpreter = call_id
                        kernel_id = await self.lazy_init_kernel(session_id, session_state)

                        # 3. 执行代码
                        req = ExecuteRequest(kernel_id=kernel_id, code=code, mode="full", msg_id=call_id)
                        code_request = SendTaskStreamingRequest(
                            id=request.id,
                            params=TaskSendParams(
                                id=call_id,
                                sessionId=session_id,
                                payload=req.model_dump(),
                                acceptedOutputModes=task_send_params.acceptedOutputModes,
                                pushNotification=task_send_params.pushNotification,
                                metadata=task_send_params.metadata,
                            ),
                        )
                        call_response_stream = code_task_manager.on_send_task_subscribe(code_request)
                    else:
                        # 3. 执行工具调用
                        tool_request = SendTaskRequest(
                            id=request.id,
                            params=TaskSendParams(
                                id=call_id,
                                sessionId=session_id,
                                payload={
                                    "call_name": call_name,
                                    "call_args": call_args,
                                },
                                acceptedOutputModes=task_send_params.acceptedOutputModes,
                                pushNotification=task_send_params.pushNotification,
                                metadata=task_send_params.metadata,
                            ),
                        )
                        call_response_stream = tool_task_manager.on_send_task_subscribe(tool_request)
                    call_response_streams.append(call_response_stream)

                # 4. 处理执行结果
                call_id_to_message_content: dict[str, list[DialogData]] = defaultdict(list)
                async for call_response in merge_streams(*call_response_streams):
                    if isinstance(call_response, SendTaskStreamingResponse):
                        if isinstance(call_response.result, TaskStatusUpdateEvent):
                            call_id = call_response.id
                            metadata = call_response.result.metadata
                            if metadata:
                                # 要求：
                                # 1. 及时把 streaming response 返回给前端
                                # 2. 记录执行结果到上下文，按照 call_id 区分
                                metadata["msg_key"] = msg_key
                                metadata["current_step"] = current_step
                                if call_id_for_code_interpreter and call_id == call_id_for_code_interpreter:
                                    metadata["key"] = f"{msg_key}_code_result_msg_{current_step}"
                                else:
                                    metadata["key"] = f"{msg_key}_tool_result_msg_{current_step}"

                                message_content_delta = metadata.pop("message_content", [])
                                if message_content_delta:
                                    call_id_to_message_content[call_id].extend(message_content_delta)

                                yield call_response

                # 5. 记录工具调用结果到上下文
                for call_id, message_content in call_id_to_message_content.items():
                    if call_id_for_code_interpreter and call_id == call_id_for_code_interpreter:
                        thought_messages.append({"role": "tool", "content": [{"type": "text", "text": "The execution results of CodeInterpreter will be provided by the user as following:"}], "tool_call_id": call_id})
                        if not message_content:
                            message_content = [{"type": "text", "text": "ok"}]
                        message_content.append({"type": "text", "text": "The execution results of CodeInterpreter are provided as above."})
                        thought_messages.append({"role": "user", "content": message_content})
                    else:
                        thought_messages.append({"role": "tool", "content": message_content, "tool_call_id": call_id})
            else:
                # 没有调工具就是回答了
                response_content = [{"type": "text", "text": remove_thoughts(response)}]

                yield SendTaskStreamingResponse(
                    id=request.id,
                    result=TaskArtifactUpdateEvent(
                        id=task_send_params.id,
                        metadata={
                            "block_list": response_content,
                            "msg_key": msg_key,
                            "key": f"{msg_key}_assistant_answer_{current_step}",
                        },
                    ),
                )

                history_messages.append({"role": "assistant", "content": response_content})
                break
        yield SendTaskStreamingResponse(
            id=request.id,
            result=TaskStatusUpdateEvent(
                id=task_send_params.id,
                status=TaskStatus(state=TaskState.COMPLETED),
                final=True,
            ),
        )

    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> AsyncIterable[SendTaskStreamingResponse] | JSONRPCResponse:
        await self.upsert_task(request.params)
        return self._stream_generator(request)

    async def on_send_task(self, request):
        return await super().on_send_task(request)

    async def on_get_task(self, request):
        return await super().on_get_task(request)

    async def on_cancel_task(self, request):
        return await super().on_cancel_task(request)

    async def on_get_task_push_notification(self, request):
        return await super().on_get_task_push_notification(request)

    async def on_resubscribe_to_task(self, request):
        return await super().on_resubscribe_to_task(request)

    async def on_set_task_push_notification(self, request):
        return await super().on_set_task_push_notification(request)


async def _process_request(task_manager: TaskManager, request: Request):
    print("Processing request")
    try:
        body = await request.json()
        json_rpc_request: TaskRequest = A2ARequest.validate_python(body)
        if isinstance(json_rpc_request, GetTaskRequest):
            result = await task_manager.on_get_task(json_rpc_request)
        elif isinstance(json_rpc_request, SendTaskRequest):
            result = await task_manager.on_send_task(json_rpc_request)
        elif isinstance(json_rpc_request, SendTaskStreamingRequest):
            result = await task_manager.on_send_task_subscribe(json_rpc_request)
        elif isinstance(json_rpc_request, CancelTaskRequest):
            result = await task_manager.on_cancel_task(json_rpc_request)
        elif isinstance(json_rpc_request, SetTaskPushNotificationRequest):
            result = await task_manager.on_set_task_push_notification(json_rpc_request)
        elif isinstance(json_rpc_request, GetTaskPushNotificationRequest):
            result = await task_manager.on_get_task_push_notification(json_rpc_request)
        elif isinstance(json_rpc_request, TaskResubscriptionRequest):
            result = await task_manager.on_resubscribe_to_task(json_rpc_request)
        else:
            logger.warning(f"Unexpected request type: {type(json_rpc_request)}")
            raise ValueError(f"Unexpected request type: {type(request)}")
        return _create_response(result)

    except Exception as e:
        logger.error(f"traceback --> {traceback.format_exc()}")
        logger.error(f"Error processing request: {e}")
        return _handle_exception(e)


def _create_response(result: Any) -> JSONResponse | EventSourceResponse:
    if isinstance(result, AsyncIterable):

        async def event_generator(result: AsyncIterable[BaseModel]) -> AsyncIterable[dict[str, str]]:
            async for item in result:
                yield {"data": item.model_dump_json(exclude_none=True)}

        return EventSourceResponse(event_generator(result))

    elif isinstance(result, JSONRPCResponse):
        return JSONResponse(result.model_dump(exclude_none=True))

    else:
        logger.error(f"Unexpected result type: {type(result)}")
        raise ValueError(f"Unexpected result type: {type(result)}")


def _handle_exception(e: Exception) -> JSONResponse:
    if isinstance(e, json.decoder.JSONDecodeError):
        json_rpc_error = JSONParseError()
    elif isinstance(e, ValidationError):
        json_rpc_error = InvalidRequestError(data=json.loads(e.json()))
    else:
        logger.error(f"Unhandled exception: {e}")
        json_rpc_error = InternalError()

    response = JSONRPCResponse(id=None, error=json_rpc_error)
    return JSONResponse(response.model_dump(exclude_none=True), status_code=400)
