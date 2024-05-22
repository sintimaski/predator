from app.consts import M
from app.dispatcher.dispatcher import EventSchema
from app.dispatcher.events.base import BaseEvent
from app.logger import logger
from app.rp_encoder import rpe


class EventPong(BaseEvent):
    def process(self):
        # logger.debug(f"S: {event.client_address} {M.PONG}")
        pass
