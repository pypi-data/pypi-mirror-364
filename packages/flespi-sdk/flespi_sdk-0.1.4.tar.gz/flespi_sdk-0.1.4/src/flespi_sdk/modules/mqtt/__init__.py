import urllib.parse

import aiohttp
from flespi_sdk.modules.flespi_session import FlespiSession


class MQTT(FlespiSession):
    def __init__(self, session: aiohttp.ClientSession, cid: int | None = None):
        super().__init__(session, cid)

    async def list(self, topic: str):
        """
        Get messages from the specified MQTT topic.
        :param topic: The MQTT topic to get messages from.
        :return: List of messages from the specified topic.
        """
        params = {"fields": "cid,topic,payload,user_properties"}
        async with self.session.get(
            f"/mqtt/messages/{urllib.parse.quote_plus(topic)}",
            params=params,
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            direct_messages = [msg for msg in result if msg["cid"] == self.cid]
            for msg in direct_messages:
                del msg["cid"]
            return direct_messages

    async def get(self, topic: str):
        """
        Get a specific message from the specified MQTT topic.
        :param topic: The MQTT topic to get the message from.
        :return: The message from the specified topic.
        """
        msgs = await self.list(topic)
        if len(msgs) > 1:
            raise ValueError(
                f"Multiple messages found for topic '{topic}'. Use list() to get all messages."
            )
        elif len(msgs) == 0:
            raise ValueError(f"No messages found for topic '{topic}'.")
        else:
            return msgs[0]

    async def publish(
        self, topic: str, payload: str | None = None, retained: bool = False
    ):
        """
         Publish a message to the specified MQTT topic.
        :param topic: The MQTT topic to publish the message to.
        :param payload: The message payload.
        :param retained: Whether the message should be retained.
        """
        message = {
            "topic": topic,
            "retained": retained,
            "payload": payload,
        }
        async with self.session.post(
            "/mqtt/messages",
            json=message,
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            return result

    async def delete(self, topic: str):
        """
        Delete a message from the specified MQTT topic.
        :param topic: The MQTT topic to delete the message from.
        """
        async with self.session.delete(
            f"/mqtt/messages/{urllib.parse.quote_plus(topic)}",
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            return result
