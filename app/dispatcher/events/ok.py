from app.dispatcher.dispatcher import EventSchema
from app.dispatcher.events.base import BaseEvent
from app.rp_encoder import rpe
from app.consts import M


class EventOk(BaseEvent):
    def process(self):
        pass
