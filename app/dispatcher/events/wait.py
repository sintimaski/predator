from app.config import cfg
from app.dispatcher.event_schema import EventSchema
from app.dispatcher.events.base import BaseEvent
from app.logger import logger
from app.rp_encoder import rpe


class EventWait(BaseEvent):
    async def process(self):
        if cfg.is_master:
            from app.predator import predator

            if not predator.write_received:
                await self.write(rpe.integer(len(predator.replicas)))
                logger.debug("Wait")
                return

            amount = int(self.event.data[1])
            amount = (
                amount if amount <= len(predator.replicas) else len(predator.replicas)
            )

            predator.wait_amount = amount

            timeout = int(self.event.data[2])
            await predator.make_wait(amount, timeout, self.writer)

            await self.write(rpe.integer(predator.wait_responded))

            predator.wait_amount = 0
            predator.wait_responded = 0
        logger.debug("Wait")
