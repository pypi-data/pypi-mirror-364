from typing_extensions import Any, AsyncGenerator, Union, AsyncIterable
import asyncio

import openai
from agentlin.core.types import *
from agentlin.core.agent_schema import AgentCore
from agentlin.route.task_manager import InMemoryTaskManager


class AgentTaskManager(InMemoryTaskManager):
    def __init__(
        self,
        agent: AgentCore,
    ):
        super().__init__()
        self.agent = agent
        self.client = openai.AsyncOpenAI()

    async def _stream_generator(self, request: SendTaskStreamingRequest) -> AsyncGenerator[SendTaskStreamingResponse | JSONRPCResponse, Any]:
        task_send_params: TaskSendParams = request.params
        payload = task_send_params.payload
        session_id = task_send_params.sessionId
        history_messages: list[DialogData] = payload["history_messages"]
        inference_args: dict = payload.get("inference_args", {})

        # 获取OpenAI配置
        model = inference_args.get("model", "gpt-4")
        max_tokens = inference_args.get("max_tokens", 10 * 1024)
        temperature = inference_args.get("temperature", 0.7)

        try:
            # 发送任务状态更新 - 开始处理
            yield SendTaskStreamingResponse(
                id=request.id,
                result=TaskStatusUpdateEvent(
                    id=task_send_params.id,
                    status=TaskStatus(state=TaskState.WORKING),
                ),
            )

            # 调用OpenAI流式API
            stream = await self.client.chat.completions.create(
                model=model,
                messages=history_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )

            collected_response = ""

            # 处理流式响应
            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        collected_response += delta.content

                        # 发送增量内容更新
                        yield SendTaskStreamingResponse(
                            id=request.id,
                            result=TaskArtifactUpdateEvent(
                                id=task_send_params.id,
                                metadata={
                                    "delta": delta.content,
                                }
                            ),
                        )

            # 更新任务状态为完成
            task = await self.update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.COMPLETED),
                collected_response,
            )

            # 发送最终完成响应
            yield SendTaskStreamingResponse(
                id=request.id,
                result=TaskStatusUpdateEvent(
                    id=task_send_params.id,
                    final=True,
                    status=TaskStatus(state=TaskState.COMPLETED),
                    metadata={
                        "final_response": collected_response,
                    }
                ),
            )

        except Exception as e:
            # 处理错误情况
            error_message = f"处理请求时发生错误: {str(e)}"

            # 更新任务状态为失败
            await self.update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.FAILED),
                {"error": error_message},
            )

            # 发送错误响应
            yield JSONRPCResponse(
                id=request.id,
                error=JSONRPCError(
                    code=-32000,
                    message=error_message
                )
            )


    def _validate_request(self, request: Union[SendTaskRequest, SendTaskStreamingRequest]):
        task_send_params: TaskSendParams = request.params
        if not are_modalities_compatible(task_send_params.acceptedOutputModes, self.agent.SUPPORTED_CONTENT_TYPES):
            return JSONRPCResponse(id=request.id, error=ContentTypeNotSupportedError())

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        error = self._validate_request(request)
        if error:
            return error
        await self.upsert_task(request.params)
        return await self._invoke(request)

    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> AsyncIterable[SendTaskStreamingResponse] | JSONRPCResponse:
        error = self._validate_request(request)
        if error:
            return error
        await self.upsert_task(request.params)
        return self._stream_generator(request)

    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        task_send_params: TaskSendParams = request.params
        payload = task_send_params.payload
        session_id = task_send_params.sessionId
        history_messages: list[DialogData] = payload["history_messages"]
        inference_args: dict = payload.get("inference_args", {})
        response = self.agent.inference(history_messages, **inference_args)
        task = await self.update_store(
            task_send_params.id,
            TaskStatus(state=TaskState.COMPLETED),
            response,
        )
        return SendTaskResponse(id=request.id, result=task)
