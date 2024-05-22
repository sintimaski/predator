from app.config import cfg
from app.dispatcher.events.base import BaseEvent
from app.logger import logger
from app.rp_encoder import rpe


class EventConfig(BaseEvent):
    async def process(self):
        name = self.event.data[2]
        value = cfg.get(name)
        await self.write(rpe.array([name, value]))
        logger.debug("Event Config")
