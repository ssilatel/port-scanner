from collections.abc import Collection
from concurrent.futures import ThreadPoolExecutor
from src.types import PortStatus, Port, ScanResults
from threading import Lock
import socket


class TCPScanner:
    def __init__(
            self,
            target: str,
            ports: Collection[int],
            timeout: float,
            output_file: str
        ):
        self.target = target
        self.ports = ports
        self.timeout = timeout
        self.output_file = output_file
        self.scan_results = ScanResults([])
        self.observers = []
        self.lock = Lock()

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self):
        for observer in self.observers:
            observer.update()
    
    def scan_single_port(self, port):
        with self.lock:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    sock.settimeout(self.timeout)
                    sock.connect((self.target, port))
                except socket.gaierror:
                    raise SystemExit(
                        f"Failed to connect or resolve hostname to target "
                        f"address {self.target}"
                    )
                except socket.timeout:
                    self.scan_results.ports.append(Port(port, PortStatus.TIMEOUT))
                    self.notify()
                except ConnectionRefusedError:
                    self.scan_results.ports.append(Port(port, PortStatus.CONN_REFUSED))
                    self.notify()
                else:
                    self.scan_results.ports.append(Port(port, PortStatus.OPEN))
                    self.notify()

    def scan_ports(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.scan_single_port, self.ports)
