import asyncio
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse

from app.logger import logger
from app.config import cfg
from app.helpers import generate_random_string


async def main():
    set_config()
    if not cfg.replicaof:
        from app.predator import predator

        _predator = predator
        await _predator.run()
    else:
        from app.predator_replica import PredatorReplica

        async with PredatorReplica() as replica:
            await replica.run()


def set_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=6379)
    parser.add_argument("--replicaof", type=str, default=None)
    parser.add_argument("--dir", type=str, default=None)
    parser.add_argument("--dbfilename", type=str, default=None)

    args = parser.parse_args()

    cfg.set("port", args.port)
    cfg.set("address", args.address)

    cfg.set("dir", args.dir)
    cfg.set("dbfilename", args.dbfilename)

    cfg.set("replicaof", args.replicaof)
    cfg.set("master_replid", generate_random_string())
    cfg.set("master_repl_offset", 0)

    if args.replicaof:
        cfg.set("role", "slave")
        cfg.set("is_master", False)
    else:
        cfg.set("role", "master")
        cfg.set("is_master", True)


if __name__ == "__main__":
    asyncio.run(main())
