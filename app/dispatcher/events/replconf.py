import asyncio

from app.dispatcher.events.base import BaseEvent
from app.logger import logger
from app.rp_encoder import rpe
from app.consts import M
from app.config import cfg


class EventReplConf(BaseEvent):
    async def listening_port(self):
        cfg.set("listening_port", self.event.data[2])
        from app.predator import predator

        await predator.add_replica(self.event.sock, self.event.sock_reader)

        logger.debug(f"S: {self.event.client_address} REPLICA ADDED")

        await self.write(rpe.simple_string(M.OK))

    async def getack(self):
        if self.event.data[2] == "*":
            await self.write(
                rpe.array(
                    M.REPLCONF_ACK.format(self.event.server_instance.offset).split()
                ),
                False,
            )
            self.event.server_instance.offset += len(rpe.array(self.event.data))
            logger.debug(f"S: {self.event.client_address} REPLCONF GETACK")
        else:
            await asyncio.sleep(0)

    async def process(self):
        if self.event.data[1] == "listening-port":
            await self.listening_port()

        elif self.event.data[1] == "capa":
            cfg.set("capa", self.event.data[2])
            await self.write(rpe.simple_string(M.OK))

        elif self.event.data[1].upper() == "GETACK":
            await self.getack()

        elif self.event.data[1].upper() == "ACK":
            from app.predator import predator
            predator.wait_responded += 1
