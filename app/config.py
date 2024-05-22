from typing import Optional, Any, List, Tuple
from dataclasses import dataclass
from dataclasses import fields, asdict

from typing import Literal

from app.helpers import singleton

Role = Literal["master", "slave"]


@singleton
@dataclass
class Config:
    address: str = "localhost"
    port: int = 6379

    role: Role = None
    replicaof: str | None = None
    master_replid: str | None = None
    master_repl_offset: int = 0
    listening_port: int | None = None
    capa: str | None = None
    is_master: bool = False
    dir: str | None = None
    dbfilename: str | None = None

    def set(self, name: str, value: Any) -> None:
        setattr(self, name, value)

    def get(self, name: str) -> Any:
        return getattr(self, name)

    def get_fields(self) -> List[str]:
        return [field.name for field in fields(self)]

    def get_values(self) -> List[Any]:
        return list(asdict(self).values())

    def get_items(self) -> List[Tuple[str, Any]]:
        return list(asdict(self).items())


cfg = Config()
