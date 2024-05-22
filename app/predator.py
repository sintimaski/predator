import time

from app.config import cfg
from app.dispatcher.dispatcher import dispatcher
from app.helpers import singleton
from app.logger import logger

import asyncio

from app.rp_encoder import rpe


# @singleton
class Predator:
    def __init__(self):
        logger.debug("Starting server")
        self.port = cfg.port
        self.address = cfg.address
        self.server = None

        self.replicas = []
        self._replicas = {}

        self.backlog_resp = {}

        self.offset = 0

        self.on_wait = False
        self.wait_amount = 0
        self.wait_responded = 0
        self.write_cb_writer = None
        self.write_received = False

    async def add_replica(
        self, sock: asyncio.StreamWriter, sock_reader: asyncio.StreamReader
    ) -> None:
        self.replicas.append(sock)
        self._replicas[sock] = {
            "writer": sock,
            "reader": sock_reader,
            "address": sock.get_extra_info("peername"),
            "offset": 0,
            "checked": False,
        }

    async def collect_wait(self, timeout):
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            if self.wait_amount - self.wait_responded <= 0:
                break
            await asyncio.sleep(0.1)

    async def make_wait(self, amount, timeout, write_cb_writer):
        self.wait_responded = 0
        self.wait_amount = amount
        self.write_cb_writer = write_cb_writer

        for replica in self.replicas:
            replica.write(rpe.array(["REPLCONF", "GETACK", "*"]))

        await asyncio.create_task(self.collect_wait(timeout))

    async def run(self):
        self.server = await asyncio.start_server(
            self.handle_client, cfg.address, cfg.port
        )

        async with self.server:
            await self.server.serve_forever()

    async def handle_client(self, reader, writer):
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                await self.handle_client_data(reader, writer, data)
        finally:
            writer.close()
            await writer.wait_closed()

    async def handle_client_data(self, reader, writer, data):
        if data:
            await dispatcher.dispatch(
                data=data,
                sock_reader=reader,
                sock_writer=writer,
                replicas=self.replicas,
                server_instance=self,
            )
        else:
            logger.debug("Connection closed")
            writer.close()


predator = Predator()
