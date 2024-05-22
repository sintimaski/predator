import asyncio
import inspect
from typing import Callable

from app.config import cfg
from app.database import db
from app.dispatcher.event_schema import EventSchema
from app.rp_encoder import rpe
from app.rp_parser import RedisProtocolParser
from app.logger import logger
import app.dispatcher.events as ev
from app.consts import WRITE_COMMANDS, M, READ_COMMANDS


class PredatorDispatcher:
    def __init__(self):
        self.handlers = {}
        self.parser = RedisProtocolParser()

    def add_handler(self, event_type: str, handler) -> None:
        event_type = event_type.upper()
        if event_type not in self.handlers:
            self.handlers[event_type] = []
            self.handlers[event_type.encode()] = []
        self.handlers[event_type].append(handler)
        self.handlers[event_type.encode()].append(handler)

    def remove_handler(self, event_type: str, handler: Callable[..., None]) -> None:
        event_type = event_type.upper()
        if event_type in self.handlers and handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)

    @staticmethod
    async def propagate(responses, replicas):
        for response in responses:
            if response[0] in WRITE_COMMANDS:
                logger.debug(f"S: propagating WRITE_COMMANDS {response}")
                from app.predator import predator
                predator.write_received = True
                for writer in replicas:
                    writer.write(rpe.array(response))
                    await writer.drain()

    async def dispatch(
        self,
        data,
        sock_reader,
        sock_writer,
        replicas=None,
        server_instance=None,
    ) -> None:

        client_address = sock_writer.get_extra_info("peername")

        responses = self.parser.parse(data)
        if responses is None or len(responses) == 0:
            return

        if cfg.is_master:
            await self.propagate(responses, replicas)

        if not isinstance(responses[0], list):
            responses = [responses]

        logger.debug(f"R: {client_address} {responses}")

        for response in responses:
            if isinstance(response[0], bytes) and response[0].startswith(b"REDIS"):
                continue
            elif (
                isinstance(response[0], str)
                and response != M.REPLCONF_GETACK.format("*").split()
            ):
                self.add_to_offset_replica(server_instance, rpe.array(response))

            logger.debug(f"R: {client_address} {response}")

            event_type = response[0].upper()
            if event_type in self.handlers:
                await self.send_event(
                    event_type,
                    response,
                    client_address,
                    sock_writer,
                    sock_reader,
                    server_instance,
                )
            else:
                logger.error(f"Invalid event type: {event_type}")

    async def send_event(
        self,
        event_type,
        response,
        client_address,
        sock_writer,
        sock_reader,
        server_instance,
    ):
        event = EventSchema(
            event_type=event_type,
            data=response,
            client_address=client_address,
            sock=sock_writer,
            sock_reader=sock_reader,
            is_master=cfg.is_master,
            server_instance=server_instance,
        )
        for handler in self.handlers[event_type]:
            handler_instance = handler(event)
            if inspect.iscoroutinefunction(handler_instance.process):
                await handler_instance.process()
            else:
                handler_instance.process()

    @staticmethod
    def add_to_offset_replica(server_instance, data):
        if not cfg.is_master and server_instance.offset > 0:
            server_instance.offset += len(data)


dispatcher = PredatorDispatcher()

dispatcher.add_handler("PING", ev.EventPing)
dispatcher.add_handler("PONG", ev.EventPong)
dispatcher.add_handler("ECHO", ev.EventEcho)
dispatcher.add_handler("GET", ev.EventGet)
dispatcher.add_handler("SET", ev.EventSet)
dispatcher.add_handler("INFO", ev.EventInfo)
dispatcher.add_handler("REPLCONF", ev.EventReplConf)
dispatcher.add_handler("PSYNC", ev.EventPSync)
dispatcher.add_handler("OK", ev.EventOk)
dispatcher.add_handler("FULLRESYNC", ev.EventFullResync)
dispatcher.add_handler("WAIT", ev.EventWait)
dispatcher.add_handler("CONFIG", ev.EventConfig)
