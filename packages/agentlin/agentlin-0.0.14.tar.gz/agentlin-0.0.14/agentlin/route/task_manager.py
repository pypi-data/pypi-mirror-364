from abc import ABC, abstractmethod
from typing_extensions import Union, AsyncIterable, List
from loguru import logger
import asyncio

from agentlin.core.types import *


class TaskManager(ABC):
    @abstractmethod
    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        pass

    @abstractmethod
    async def on_cancel_task(self, request: CancelTaskRequest) -> CancelTaskResponse:
        pass

    @abstractmethod
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        pass

    @abstractmethod
    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> Union[AsyncIterable[SendTaskStreamingResponse], JSONRPCResponse]:
        pass

    @abstractmethod
    async def on_set_task_push_notification(self, request: SetTaskPushNotificationRequest) -> SetTaskPushNotificationResponse:
        pass

    @abstractmethod
    async def on_get_task_push_notification(self, request: GetTaskPushNotificationRequest) -> GetTaskPushNotificationResponse:
        pass

    @abstractmethod
    async def on_resubscribe_to_task(self, request: TaskResubscriptionRequest) -> Union[AsyncIterable[SendTaskResponse], JSONRPCResponse]:
        pass


class InMemoryTaskManager(TaskManager):
    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.push_notification_infos: dict[str, PushNotificationConfig] = {}
        self.lock = asyncio.Lock()
        self.task_sse_subscribers: dict[str, List[asyncio.Queue]] = {}
        self.subscriber_lock = asyncio.Lock()

    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        logger.info(f"Getting task {request.params.id}")
        task_query_params: TaskQueryParams = request.params

        async with self.lock:
            task = self.tasks.get(task_query_params.id)
            if task is None:
                return GetTaskResponse(id=request.id, error=TaskNotFoundError())

        return GetTaskResponse(id=request.id, result=task)

    async def on_cancel_task(self, request: CancelTaskRequest) -> CancelTaskResponse:
        logger.info(f"Cancelling task {request.params.id}")
        task_id_params: TaskIdParams = request.params

        async with self.lock:
            task = self.tasks.get(task_id_params.id)
            if task is None:
                return CancelTaskResponse(id=request.id, error=TaskNotFoundError())

        return CancelTaskResponse(id=request.id, error=TaskNotCancelableError())

    @abstractmethod
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        pass

    @abstractmethod
    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> Union[AsyncIterable[SendTaskStreamingResponse], JSONRPCResponse]:
        pass

    async def set_push_notification_info(self, task_id: str, notification_config: PushNotificationConfig):
        async with self.lock:
            task = self.tasks.get(task_id)
            if task is None:
                raise ValueError(f"Task not found for {task_id}")

            self.push_notification_infos[task_id] = notification_config

        return

    async def get_push_notification_info(self, task_id: str) -> PushNotificationConfig:
        async with self.lock:
            task = self.tasks.get(task_id)
            if task is None:
                raise ValueError(f"Task not found for {task_id}")

            return self.push_notification_infos[task_id]

        return

    async def has_push_notification_info(self, task_id: str) -> bool:
        async with self.lock:
            return task_id in self.push_notification_infos

    async def on_set_task_push_notification(self, request: SetTaskPushNotificationRequest) -> SetTaskPushNotificationResponse:
        logger.info(f"Setting task push notification {request.params.id}")
        task_notification_params: TaskPushNotificationConfig = request.params

        try:
            await self.set_push_notification_info(
                task_notification_params.id,
                task_notification_params.pushNotificationConfig,
            )
        except Exception as e:
            logger.error(f"Error while setting push notification info: {e}")
            return JSONRPCResponse(
                id=request.id,
                error=InternalError(message="An error occurred while setting push notification info"),
            )

        return SetTaskPushNotificationResponse(
            id=request.id,
            result=task_notification_params,
        )

    async def on_get_task_push_notification(self, request: GetTaskPushNotificationRequest) -> GetTaskPushNotificationResponse:
        logger.info(f"Getting task push notification {request.params.id}")
        task_params: TaskIdParams = request.params

        try:
            notification_info = await self.get_push_notification_info(task_params.id)
        except Exception as e:
            logger.error(f"Error while getting push notification info: {e}")
            return GetTaskPushNotificationResponse(
                id=request.id,
                error=InternalError(message="An error occurred while getting push notification info"),
            )

        return GetTaskPushNotificationResponse(
            id=request.id,
            result=TaskPushNotificationConfig(id=task_params.id, pushNotificationConfig=notification_info),
        )

    async def upsert_task(self, task_send_params: TaskSendParams) -> Task:
        logger.info(f"Upserting task {task_send_params.id}")
        async with self.lock:
            task = self.tasks.get(task_send_params.id)
            if task is None:
                task = Task(
                    id=task_send_params.id,
                    sessionId=task_send_params.sessionId,
                    status=TaskStatus(state=TaskState.SUBMITTED),
                )
                self.tasks[task_send_params.id] = task

            return task

    async def on_resubscribe_to_task(self, request: TaskResubscriptionRequest) -> Union[AsyncIterable[SendTaskStreamingResponse], JSONRPCResponse]:
        return JSONRPCResponse(id=request.id, error=UnsupportedOperationError())

    async def update_store(self, task_id: str, status: TaskStatus, metadata: Optional[dict]=None) -> Task:
        async with self.lock:
            try:
                task = self.tasks[task_id]
            except KeyError:
                logger.error(f"Task {task_id} not found for updating the task")
                raise ValueError(f"Task {task_id} not found")

            task.status = status
            if metadata is not None:
                task.metadata = metadata
            return task

    async def setup_sse_consumer(self, task_id: str, is_resubscribe: bool = False):
        async with self.subscriber_lock:
            if task_id not in self.task_sse_subscribers:
                if is_resubscribe:
                    raise ValueError("Task not found for resubscription")
                else:
                    self.task_sse_subscribers[task_id] = []

            sse_event_queue = asyncio.Queue(maxsize=0)  # <=0 is unlimited
            self.task_sse_subscribers[task_id].append(sse_event_queue)
            return sse_event_queue

    async def enqueue_events_for_sse(self, task_id, task_update_event):
        async with self.subscriber_lock:
            if task_id not in self.task_sse_subscribers:
                return

            current_subscribers = self.task_sse_subscribers[task_id]
            for subscriber in current_subscribers:
                await subscriber.put(task_update_event)

    async def dequeue_events_for_sse(self, request_id, task_id, sse_event_queue: asyncio.Queue) -> AsyncIterable[SendTaskStreamingResponse] | JSONRPCResponse:
        try:
            while True:
                event = await sse_event_queue.get()
                if isinstance(event, JSONRPCError):
                    yield SendTaskStreamingResponse(id=request_id, error=event)
                    break

                yield SendTaskStreamingResponse(id=request_id, result=event)
                if isinstance(event, TaskStatusUpdateEvent) and event.final:
                    break
        finally:
            async with self.subscriber_lock:
                if task_id in self.task_sse_subscribers:
                    self.task_sse_subscribers[task_id].remove(sse_event_queue)


async def merge_streams(*streams):
    """
    Merges multiple asynchronous streams into a single stream.

    Args:
        *streams: Asynchronous streams to merge.
    Yields:
        Items from the merged streams.
    Example:
        async for item in merge_streams(stream1, stream2):
            process(item)
    """
    queue = asyncio.Queue()

    # 为每个输入流启动一个协程，将元素放入队列
    async def feed_queue(stream):
        async for item in stream:
            await queue.put(item)

    tasks = [asyncio.create_task(feed_queue(stream)) for stream in streams]

    # 消费队列中的元素，直到所有流都结束
    active_streams = len(streams)
    while active_streams > 0:
        item = await queue.get()
        if item is None:
            active_streams -= 1
            continue
        yield item

    # 确保所有任务都完成
    await asyncio.gather(*tasks)
