import json
from dataclasses import dataclass


@dataclass
class Message:
    data: bytes
    attributes: dict[str, str]
    message_id: str
    delivery_attempt: int
    ack_id: str

    @property
    def json(self):
        return json.loads(self.data)
