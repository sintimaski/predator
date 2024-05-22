import asyncio

from app.dispatcher.event_schema import EventSchema


class BaseEvent:
    def __init__(self, event: EventSchema):
        self.writer = event.sock
        self.server_instance = event.server_instance
        self.is_master = event.is_master
        self.event = event

    async def process(self):
        raise NotImplementedError

    async def write(self, message, add=True):
        self.writer.write(message)
        if self.is_master and self.server_instance.offset > 0 and add:
            self.server_instance.offset += len(message)
        await self.writer.drain()
