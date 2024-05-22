from dataclasses import dataclass
from typing import List, Any, Tuple

from app.rp_encoder import rpe


@dataclass
class EventSchema:
    data: List[Any]
    client_address: Tuple[str, int]
    sock: Any
    sock_reader: Any
    event_type: str
    is_master: bool
    server_instance: Any
