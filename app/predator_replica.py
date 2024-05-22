import asyncio
from asyncio import sleep, get_event_loop
from typing import AsyncIterator

from app.config import cfg
from app.database import db
from app.dispatcher.dispatcher import dispatcher
from app.logger import logger
from app.helpers import singleton
from app.consts import M
from app.predator import Predator
from app.rp_encoder import rpe


class PredatorReplica(Predator):
    def __init__(self):
        logger.debug("Starting replica server")
        super().__init__()
        self.port = cfg.port
        self.address = cfg.address
        self.replicaof = cfg.replicaof

        self.master_address = self.replicaof.split()[0]
        self.master_port = int(self.replicaof.split()[1])
        self.master_writer = None
        self.master_reader = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        if self.master_writer:
            self.master_writer.close()

    async def write(self, writer: asyncio.StreamWriter, data: bytes):
        writer.write(data)
        await writer.drain()

    async def connect_to_master(self):
        logger.debug("Connecting to master")
        self.master_reader, writer = await asyncio.open_connection(
            self.master_address, self.master_port
        )
        logger.debug(f"Connected to {writer.get_extra_info('peername')}")
        self.master_writer = writer
        await self.handshake()
        return writer

    async def send_command(self, command):
        await self.write(self.master_writer, command)
        logger.debug(f"HS resp: {await self.master_reader.readuntil(b"\r\n")}")

    async def handshake(self) -> None:
        logger.debug("Handshake initiated")

        await self.send_command(M.PING)
        await self.send_command(
            rpe.array(["REPLCONF", "listening-port", str(self.port)])
        )
        await self.send_command(rpe.array(["REPLCONF", "capa", "psync2"]))
        await self.send_command(rpe.array(["PSYNC", "?", "-1"]))

        res: bytes = await self.master_reader.readuntil(b"\r\n")
        await self.master_reader.readexactly(int(res[1:-2]))
        logger.debug("Handshake read kickoff completed")
        logger.debug("Handshake completed")

        await self.receive_commands()

    async def run(self):
        server = await asyncio.start_server(self.handle_client, cfg.address, cfg.port)
        _ = asyncio.create_task(self.connect_to_master())

        async with server:
            await server.serve_forever()

    async def receive_commands(self) -> None:
        addr = self.master_writer.get_extra_info("peername")
        try:
            while requestobj := await self.master_reader.read(1024):
                await dispatcher.dispatch(
                    data=requestobj,
                    sock_reader=self.master_reader,
                    sock_writer=self.master_writer,
                    replicas=self.replicas,
                    server_instance=self,
                )
        except ConnectionResetError:
            logger.error(f"Connection reset by peer: {addr}")
        except Exception as e:
            logger.error(f"Error handling client {addr}: {e}")
