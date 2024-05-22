# MESSAGES
class M:
    OK = "OK"
    NULL = b"$-1\r\n"

    PING = b"*1\r\n$4\r\nPING\r\n"
    PONG = "PONG"

    FULLRESYNC = "FULLRESYNC {repl_id} 0"
    REPLCONF_ACK = "REPLCONF ACK {}"
    REPLCONF_GETACK = "REPLCONF GETACK {}"


WRITE_COMMANDS = ["SET", "DEL"]
READ_COMMANDS = ["GET"]
REPLCONF_ACK_s = b"*"
