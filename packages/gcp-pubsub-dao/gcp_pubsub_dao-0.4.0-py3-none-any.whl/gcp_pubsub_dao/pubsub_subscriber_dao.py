from google.cloud.pubsub_v1 import SubscriberClient

from gcp_pubsub_dao.entities import Message


class PubSubSubscriberDAO:
    def __init__(self, project_id: str, subscription_id: str):
        self.subscriber = SubscriberClient()
        self.project_id = project_id
        self.subscription_id = subscription_id

    def get_topic_name_by_subscription_id(self, subscription_id: str) -> str:
        subscription = self.subscriber.get_subscription(
            request={
                "subscription": self.subscriber.subscription_path(self.project_id, subscription_id),
            },
        )

        return subscription.topic.rsplit("/", 1)[1]

    def get_messages(self, messages_count: int, return_immediately: bool = False) -> list[Message]:
        response = self.subscriber.pull(
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

    def ack_messages(self, ack_ids: list[str]) -> None:
        self.subscriber.acknowledge(
            request={
                "subscription": self.subscriber.subscription_path(self.project_id, self.subscription_id),
                "ack_ids": ack_ids,
            },
        )

    def nack_messages(self, ack_ids: list[str]) -> None:
        self.subscriber.modify_ack_deadline(
            request={
                "subscription": self.subscriber.subscription_path(self.project_id, self.subscription_id),
                "ack_ids": ack_ids,
                "ack_deadline_seconds": 0,
            },
        )

    def close(self) -> None:
        self.subscriber.close()
