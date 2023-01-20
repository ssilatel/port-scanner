from collections.abc import Collection
from dataclasses import dataclass
from enum import Enum
from typing import List
import socket


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


class PortScanner:
    def __init__(self, target: str, ports: Collection[int], timeout: float):
        self.target = target
        self.ports = ports
        self.timeout = timeout
        self.scan_results = ScanResults([])

    def scan_ports(self):
        for p in self.ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    sock.settimeout(self.timeout)
                    sock.connect((self.target, p))
                except socket.gaierror:
                    raise SystemExit(
                        f"Failed to connect or resolve hostname to target "
                        f"address {self.target}"
                    )
                except socket.timeout:
                    self.scan_results.ports.append(Port(p, PortStatus.TIMEOUT))
                    yield Port(p, PortStatus.TIMEOUT)
                except ConnectionRefusedError:
                    self.scan_results.ports.append(Port(p, PortStatus.CONN_REFUSED))
                    yield Port(p, PortStatus.CONN_REFUSED)
                else:
                    self.scan_results.ports.append(Port(p, PortStatus.OPEN))
                    yield Port(p, PortStatus.OPEN)
