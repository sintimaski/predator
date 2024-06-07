import asyncio
import os
import struct
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
    with open("../dump.rdb", "rb") as file:
        dbs = bytearray(file.read())
        print(dbs)

        dbs = dbs.split(b"\xfb")[1:]
        for db in dbs:
            db = db.rsplit(b"\xfe", 1)[0]
            ht_size = db[0]
            expiry_size = db[1]

            db = db[3:]
            i = 0
            while i < len(db):
                if hex(db[i]) == "0xfc":
                    print(0xfc)
                    # i += 6
                    print(i, db[i], chr(db[i]), hex(db[i]))

                    px = ""
                    print(db[i:])
                    split = db[i:].split(b"\x00\x00\x00\x00")
                    print(split)
                    px = split[0]
                    db = split[1]
                    print(px)
                    # while hex(db[i]) != "0x0":
                    #     print(chr(db[i]))
                    #     px += chr(db[i])
                    #     i += 1
                    # print("px", px)
                # if hex(db[i]) == "0xfd":
                #     print(0xfd)
                #     i += 6
                #     print(i, db[i], chr(db[i]), hex(db[i]))
                # print(i, db[i], chr(db[i]), hex(db[i]))
                # print(db, ht_size, expiry_size)
                i += 1

        # kick off redis
        # kick off \xfa
        # split by \xfe to get databases ->
        # foreach kick off (collect) \xfb data
        # foreach iterate over all \xfd
        # foreach iterate over all \xfc
        # foreach iterate rest

        # dbs = dbs.split(b"\xfe")[1:]
        #
        # for barr in dbs:
        #     print(barr)
        #     barr = barr.split(b'\xfb', 1)[1]
        #     barr = barr.split(b'\x00', 1)[1]
        #     if barr.startswith(b"\x00"):
        #         barr = barr.split(b'\x00', 1)[1]
        #
        #     curr_index = 0
        #     curr_end_index = 0
        #     next_n_bytes = 0
        #     # print(barr[:8 + 1])
        #     while curr_end_index < len(barr) - 1:
        #         next_n_bytes = barr[curr_end_index]
        #         curr_end_index += 1
        #
        #         try:
        #             result = ""
        #             while next_n_bytes > 0:
        #                 next_n_bytes -= 1
        #                 result += chr(barr[curr_end_index])
        #                 curr_end_index += 1
        #             print(result)
        #         except:
        #             break
    asyncio.run(main())
