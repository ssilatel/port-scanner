from dataclasses import dataclass
from enum import Enum
from typing import List


class PortStatus(Enum):
    OPEN = "Open"
    TIMEOUT = "Closed | Timeout"
    CONN_REFUSED = "Closed | ConnectionRefused"


@dataclass
class Port:
    number: int
    status: str

    def __str__(self):
        return f"Port {self.number} : {self.status.value}"


@dataclass
class ScanResults:
    ports: List[Port]
