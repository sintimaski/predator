from datetime import datetime

from app.consts import M
from app.database import db
from app.dispatcher.events.base import BaseEvent
from app.logger import logger
from app.rp_encoder import rpe


class EventGet(BaseEvent):
    async def process(self):
        data = self.event.data

        name = data[1]
        entity = db.get(name)
        if entity is None:
            await self.write(M.NULL)
            logger.debug(f"S: {self.event.client_address} {name} NULL")
            return

        px = entity.get("px")
        if px and datetime.now().timestamp() - int(px) / 1000 >= entity.get("ts"):
            db.delete(name)
            await self.write(M.NULL)
            logger.debug(f"S: {self.event.client_address} {name} NULL EXPIRED")
            return

        await self.write(rpe.bulk_string(entity.get("value")))
        logger.debug(f"S: {self.event.client_address} {name} {entity.get("value")}")
