from typing import Any, Dict
from .helpers import singleton
from .rp_parser import RedisProtocolParser


@singleton
class Database:
    def __init__(self) -> None:
        self.db: Dict[str, Any] = {}

    def get(self, name: str) -> Any:
        return self.db.get(name)

    def set(self, name: str, value: Any, px: int = None, ts: float = None) -> None:
        self.db[name] = {
            "value": value,
            "px": px,
            "ts": ts,
        }

    def delete(self, name: str) -> None:
        if name in self.db:
            del self.db[name]

    def clear(self) -> None:
        self.db.clear()

    def set_from_dump(self, db_dump):
        parser = RedisProtocolParser()
        responses = parser.parse(db_dump)
        print("TODO db_dump", db_dump, responses)
        return responses


db = Database()
