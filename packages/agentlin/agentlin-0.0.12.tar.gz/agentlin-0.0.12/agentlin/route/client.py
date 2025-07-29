from typing_extensions import Any, AsyncIterable
import json

import httpx
from httpx_sse import connect_sse

from agentlin.core.types import *


class ConnectionClient:
    def __init__(self, url: str):
        self.url = url

    async def send_task(self, payload: dict[str, Any]) -> SendTaskResponse:
        payload = TaskSendParams(**payload)
        request = SendTaskRequest(params=payload)
        return SendTaskResponse(**await self._send_request(request))

    async def send_task_streaming(self, payload: dict[str, Any]) -> AsyncIterable[SendTaskStreamingResponse]:
        request = SendTaskStreamingRequest(params=payload)
        with httpx.Client(timeout=None) as client:
            with connect_sse(client, "POST", self.url, json=request.model_dump()) as event_source:
                for sse in event_source.iter_sse():
                    yield SendTaskStreamingResponse(**json.loads(sse.data))

    async def _send_request(self, request: JSONRPCRequest) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            # Image generation could take time, adding timeout
            print(f" -----> {self.url}")
            response = await client.post(self.url, json=request.model_dump(), timeout=60)
            response.raise_for_status()
            return response.json()

    async def get_task(self, payload: dict[str, Any]) -> GetTaskResponse:
        request = GetTaskRequest(params=payload)
        return GetTaskResponse(**await self._send_request(request))

    async def cancel_task(self, payload: dict[str, Any]) -> CancelTaskResponse:
        request = CancelTaskRequest(params=payload)
        return CancelTaskResponse(**await self._send_request(request))

    async def set_task_callback(self, payload: dict[str, Any]) -> SetTaskPushNotificationResponse:
        request = SetTaskPushNotificationRequest(params=payload)
        return SetTaskPushNotificationResponse(**await self._send_request(request))

    async def get_task_callback(self, payload: dict[str, Any]) -> GetTaskPushNotificationResponse:
        request = GetTaskPushNotificationRequest(params=payload)
        return GetTaskPushNotificationResponse(**await self._send_request(request))
