from app.dispatcher.event_schema import EventSchema
from app.dispatcher.events.base import BaseEvent


class EventFullResync(BaseEvent):
    def process(self):
        pass
