from datetime import datetime

from app.config import cfg
from app.consts import M
from app.database import db
from app.dispatcher.dispatcher import EventSchema
from app.dispatcher.events.base import BaseEvent
from app.logger import logger
from app.rp_encoder import rpe


class EventSet(BaseEvent):
    async def process(self):
        data = self.event.data
        name = data[1]
        value = data[2]

        value = value if isinstance(value, str) else value.decode()
        name = name if isinstance(name, str) else name.decode()

        if len(data) > 3:
            px = data[4]
            db.set(
                name,
                value=value,
                px=px,
                ts=datetime.now().timestamp(),
            )
        else:
            db.set(
                name,
                value=value,
                ts=datetime.now().timestamp(),
            )

        if self.is_master:
            await self.write(rpe.simple_string(M.OK))

        logger.debug(f"S: {self.event.client_address} {name} SET OK")
