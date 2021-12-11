import asyncio
import inspect
import json
from typing import Callable, Union

import aioredis


class RedisMessageRelay:
    """A class for relaying messages across services using redis lists and pubsub."""

    def __init__(
            self,
            name: str,
            redis_channel: Union[aioredis.Channel, str],
            redis_list: str,
            redis_pool: aioredis.Redis,
    ) -> None:
        self.name = name
        self.channel = redis_channel
        self.redis_list = redis_list

        self.redis = redis_pool

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} channel={self.channel} list={self.redis_list}>"


class RedisMessageProducer(RedisMessageRelay):

    def __init__(
            self,
            name: str,
            redis_channel: Union[aioredis.Channel, str],
            redis_list: str,
            redis_pool: aioredis.Redis,
    ) -> None:
        super().__init__(name, redis_channel, redis_list, redis_pool)

    async def relay(self, data: dict) -> int:
        """
        Push message and notify consumer.

        returns:
            - Number of subscribers the notification was delivered to.
        """
        serialised = json.dumps(data)

        await self.redis.rpush(self.redis_list, serialised)

        # Notify consumer about new message.
        subs: int = await self.redis.publish_json(
            self.channel,
            {"pushed": True}
        )
        return subs


class RedisMessageConsumer(RedisMessageRelay):

    def __init__(
            self,
            name: str,
            redis_channel: Union[aioredis.Channel, str],
            redis_list: str,
            redis_pool: aioredis.Redis,
            callback: Callable,
            loop: asyncio.AbstractEventLoop
    ) -> None:
        super().__init__(name, redis_channel, redis_list, redis_pool)

        self.callback = callback
        self.loop = loop

    async def listen(self) -> None:
        res = await self.redis.subscribe(self.channel)
        self.channel = res[0]
        await self.wait_until_message()

    async def pre_callback(self, data: dict):
        if inspect.iscoroutinefunction(self.callback):
            await self.callback(data)
            return

        self.callback(data)

    async def read_redis_list(self) -> None:
        serialised = await self.redis.lpop(self.redis_list)
        try:
            data = json.loads(serialised)
        except (json.JSONDecodeError, TypeError):
            pass
        else:
            await self.pre_callback(data)

    async def wait_until_message(self) -> None:
        """Receive message from a channel."""
        # Empty queue before receiving messages.
        queue: list = await self.redis.lrange(self.redis_list, 0, -1)
        await self.redis.delete(self.redis_list)

        for item in queue:
            await self.pre_callback(item)

        while await self.channel.wait_message():
            data = await self.channel.get_json()

            if data["pushed"]:
                await self.read_redis_list()
