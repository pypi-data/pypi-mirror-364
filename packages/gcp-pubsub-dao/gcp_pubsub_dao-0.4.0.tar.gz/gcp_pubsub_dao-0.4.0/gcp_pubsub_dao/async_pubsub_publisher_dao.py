from google.pubsub_v1 import PubsubMessage
from google.pubsub_v1.services.publisher import PublisherAsyncClient


class AsyncPubSubPublisherDAO:
    def __init__(self, project_id: str):
        self.publisher = PublisherAsyncClient()
        self.project_id = project_id

    async def publish_message(self, topic_name: str, payload: bytes, attributes: dict) -> None:
        pubsub_message = PubsubMessage(data=payload, attributes=attributes)
        await self.publisher.publish(
            topic=self.publisher.topic_path(project=self.project_id, topic=topic_name),
            messages=[pubsub_message],
        )
