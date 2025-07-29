import asyncio
import logging
import typing as t
from dataclasses import dataclass, field

from gcp_pubsub_dao.async_pubsub_subscriber_dao import AsyncPubSubSubscriberDAO
from gcp_pubsub_dao.entities import Message

logger = logging.getLogger()


@dataclass
class HandlerResult:
    ack_id: str
    is_success: bool


@dataclass
class WorkerTask:
    subscriber_dao: AsyncPubSubSubscriberDAO
    handler: t.Callable[[Message], t.Awaitable[HandlerResult]]
    batch_size: int = 10
    return_immediately: bool = False
    messages_pool: list[Message] = field(default_factory=list)


class WorkerPool:
    def __init__(self, heartbeat_func: t.Callable | None = None):
        self.heartbeat_func = heartbeat_func

    async def run(self, tasks: t.Collection[WorkerTask], mode: t.Literal["async", "sync"] = "async"):
        """
        :param tasks: Iterable object with WorkerTask instances to be run in the worker pool
        :param mode: Defines how to run the tasks. In "async" mode it will run all the tasks asynchronously.
        For instance, if you have Task1, Task2 and Task3, they can run in random order Task2 -> Task3 -> Task1
        or at the same time asynchronously. In "sync" mode the tasks will run one by one in the order you pass them.
        If you have Task1, Task2 and Task3, and you pass them to the method as (Task1, Task2, Task3), the worker will
        run them in the same order. It's important to understand, that the worker will still process messages
        inside tasks asynchronously, but it will process the tasks themselves synchronously.
        """
        if mode == "async":
            await self._run_async(tasks=tasks)
        elif mode == "sync":
            await self._run_sync(tasks=tasks)
        else:
            raise ValueError(f'Provided mode is not supported. Expected: "async" | "sync", got {mode}')

    async def _run_sync(self, tasks: t.Collection[WorkerTask]):
        while True:
            await self._load_messages(tasks)
            for task in tasks:
                self.heartbeat_func() if self.heartbeat_func else ...
                await self._process_task_messages(task)

    async def _run_async(self, tasks: t.Collection[WorkerTask]):
        async with asyncio.TaskGroup() as tg:
            for task in tasks:
                tg.create_task(self._run_worker(task=task))

    async def _run_worker(self, task: WorkerTask):
        while True:
            self.heartbeat_func() if self.heartbeat_func else ...
            await self._load_messages((task,))
            await self._process_task_messages(task=task)

    @staticmethod
    async def _load_messages_wrapper(task: WorkerTask, coroutine: t.Coroutine[t.Any, t.Any, list[Message]]):
        result = await coroutine
        task.messages_pool += result

    async def _load_messages(self, tasks: t.Collection[WorkerTask]):
        get_messages_tasks = [
            self._load_messages_wrapper(
                task,
                task.subscriber_dao.get_messages(
                    messages_count=task.batch_size,
                    return_immediately=task.return_immediately,
                ),
            )
            for task in tasks
        ]
        for coro in asyncio.as_completed(get_messages_tasks):
            try:
                await coro
            except Exception:
                logger.exception("Exception during messages fetching.")
                continue

    @staticmethod
    async def _process_task_messages(task: WorkerTask):
        ack_ids, nack_ids = [], []
        task_groups = [(message, task.handler(message)) for message in task.messages_pool]
        if not task_groups:
            return
        messages, tasks = zip(*task_groups)
        for message, coro in zip(messages, asyncio.as_completed(tasks)):
            try:
                result: HandlerResult = await coro
            except Exception:
                logger.exception(f"Exception during task processing. Ack ID: {message.ack_id}")
                continue

            if result.is_success:
                ack_ids.append(result.ack_id)
            else:
                nack_ids.append(result.ack_id)
        task.messages_pool.clear()
        if ack_ids:
            await task.subscriber_dao.ack_messages(ack_ids=ack_ids)
        if nack_ids:
            await task.subscriber_dao.nack_messages(ack_ids=nack_ids)
