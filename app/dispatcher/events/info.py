from app.config import cfg
from app.dispatcher.events.base import BaseEvent
from app.logger import logger
from app.rp_encoder import rpe


class EventInfo(BaseEvent):
    async def process(self):
        cfg_items = cfg.get_items()
        message = "\n".join([f"{x[0]}:{x[1]}" for x in cfg_items])
        await self.write(rpe.bulk_string(message))
        logger.debug(f"S: {self.event.client_address} INFO OK")
