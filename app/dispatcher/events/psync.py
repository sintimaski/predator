import asyncio
import base64

from app.config import cfg
from app.consts import M
from app.dispatcher.dispatcher import EventSchema
from app.dispatcher.events.base import BaseEvent
from app.logger import logger
from app.rp_encoder import rpe


class EventPSync(BaseEvent):
    async def process(self):
        data = self.event.data
        repl_id = cfg.master_replid if data[1] == "?" else data[1]
        message = M.FULLRESYNC.format(repl_id=repl_id)
        await self.write(rpe.simple_string(message))
        logger.debug(f"S: {self.event.client_address} {message}")

        rdb_data = bytes.fromhex(
            "524544495330303131fa0972656469732d76657205372e322e30fa0a72656469732d62697473c040fa056374696d65c26d08bc65fa08757365642d6d656dc2b0c41000fa08616f662d62617365c000fff06e3bfec0ff5aa2"
        )
        rdb_len = len(rdb_data)
        await self.write(f"${rdb_len}\r\n".encode() + rdb_data)

        logger.debug(f"S: {self.event.client_address} SYNC FILE SENT")

        # TODO REMOVE
        # await asyncio.sleep(1)
        # await self.write(rpe.array(["REPLCONF", "GETACK", "*"]))
        # await asyncio.sleep(1)
        # await self.write(rpe.array(["REPLCONF", "GETACK", "*"]))
        # await self.write(
        #     rpe.array(["SET", "pineapple", "banana"])
        #     # + rpe.array(["SET", "pineapple", "grape"])
        #     # + rpe.array(["REPLCONF", "GETACK", "*"])
        # )
        # await self.write(rpe.array(["REPLCONF", "GETACK", "*"]))
        # await self.write(rpe.array(["REPLCONF", "GETACK", "*"]))
        # await self.write(b"")
        # TODO REMOVE
