from google.pubsub_v1.services.subscriber import SubscriberAsyncClient

from gcp_pubsub_dao.entities import Message


class AsyncPubSubSubscriberDAO:
    def __init__(self, project_id: str, subscription_id: str):
        self.subscriber = SubscriberAsyncClient()
        self.project_id = project_id
        self.subscription_id = subscription_id

    async def get_messages(self, messages_count: int, return_immediately: bool = False) -> list[Message]:
        response = await self.subscriber.pull(
            request={
                "subscription": self.subscriber.subscription_path(self.project_id, self.subscription_id),
                "max_messages": messages_count,
                "return_immediately": return_immediately,
            },
        )

        messages = []
        for received_message in response.received_messages:
            message = Message(
                data=received_message.message.data,
                attributes=dict(received_message.message.attributes),
                message_id=received_message.message.message_id,
                delivery_attempt=received_message.delivery_attempt,
                ack_id=received_message.ack_id,
            )
            messages.append(message)

        return messages

    async def ack_messages(self, ack_ids: list[str]) -> None:
        await self.subscriber.acknowledge(
            request={
                "subscription": self.subscriber.subscription_path(self.project_id, self.subscription_id),
                "ack_ids": ack_ids,
            },
        )

    async def nack_messages(self, ack_ids: list[str]) -> None:
        await self.subscriber.modify_ack_deadline(
            request={
                "subscription": self.subscriber.subscription_path(self.project_id, self.subscription_id),
                "ack_ids": ack_ids,
                "ack_deadline_seconds": 0,
            },
        )
