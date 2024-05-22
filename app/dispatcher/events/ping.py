from app.consts import M
from app.dispatcher.dispatcher import EventSchema
from app.dispatcher.events.base import BaseEvent
from app.logger import logger
from app.rp_encoder import rpe


class EventPing(BaseEvent):
    async def process(self):
        if self.event.is_master:
            await self.write(rpe.simple_string(M.PONG))
            logger.debug(f"S: {self.event.client_address} {M.PONG}")
