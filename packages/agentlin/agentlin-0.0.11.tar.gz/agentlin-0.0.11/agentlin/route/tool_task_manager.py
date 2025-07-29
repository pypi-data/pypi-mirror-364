from typing_extensions import Any, AsyncGenerator
import uuid

from fastmcp import Client
from fastmcp.client.transports import ClientTransportT

from loguru import logger

from agentlin.route.task_manager import InMemoryTaskManager
from agentlin.core.types import *


class ToolTaskManager(InMemoryTaskManager):
    def __init__(self, config: ClientTransportT, callback_url: str):
        super().__init__()
        self.callback_url = callback_url
        self.client = Client(
            config,
            # elicitation_handler=self.elicitation_handler,
        )

    def set_client(self, client: Client):
        self.client = client

    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> AsyncGenerator[SendTaskStreamingResponse, None]:
        await self.upsert_task(request.params)
        task_send_params: TaskSendParams = request.params
        session_id = task_send_params.sessionId
        payload = task_send_params.payload
        call_name: str = payload.get("call_name", "unknown_function")
        call_args: dict[str, Any] = payload.get("call_args", {})

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

        try:

            result = await self.client.call_tool(
                name=call_name,
                arguments=call_args,
            )
            content = result.content
            structured_content = result.structured_content

            yield SendTaskStreamingResponse(
                id=request.id,
                result=TaskArtifactUpdateEvent(
                    id=task_send_params.id,
                    metadata={
                        "message_content": content,
                        "block_list": [
                            {"type": "json", "data": structured_content},
                        ],
                    },
                ),
            )

        except Exception as exc:
            logger.error(f"Error in tool task: {exc}")
            yield SendTaskStreamingResponse(
                id=request.id,
                error=JSONRPCError(code=-32000, message=str(exc)),
            )
            await self.update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.FAILED, payload=str(exc)),
            )
        finally:
            yield SendTaskStreamingResponse(
                id=request.id,
                result=TaskStatusUpdateEvent(
                    id=task_send_params.id,
                    status=TaskStatus(state=TaskState.COMPLETED),
                    final=True,
                ),
            )
            # Ensure the task is marked as completed or failed
            await self.update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.COMPLETED),
            )

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        await self.upsert_task(request.params)
        return await self._invoke(request)


    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        task_send_params: TaskSendParams = request.params
        session_id = task_send_params.sessionId
        payload = task_send_params.payload
        call_id: str = payload.get("call_id", f"call_{uuid.uuid4().hex}")
        call_name: str = payload.get("call_name", "unknown_function")
        call_args: dict[str, Any] = payload.get("call_args", {})

        try:
            result = await self.client.call_tool(
                name=call_name,
                arguments=call_args,
            )

            task = await self.update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.COMPLETED),
                result,
            )
            return SendTaskResponse(id=request.id, result=task)
        except Exception as exc:
            logger.error(f"Error in tool task: {exc}")
            return SendTaskResponse(id=request.id, error=JSONRPCError(code=-32000, message=str(exc)))
