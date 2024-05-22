from app.dispatcher.events.base import BaseEvent
from app.logger import logger
from app.rp_encoder import rpe


class EventEcho(BaseEvent):
    async def process(self):
        data = self.event.data
        message = data[1]
        await self.write(rpe.bulk_string(message))
        logger.debug(f"{self.event.client_address} {message}")
