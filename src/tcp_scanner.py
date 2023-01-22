from collections.abc import Collection
from concurrent.futures import as_completed, ThreadPoolExecutor
from src.types import PortStatus, Port, ScanResults
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

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self, port):
        for observer in self.observers:
            observer.update(port)
    
    def scan_single_port(self, port: int):
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
                return Port(port, PortStatus.Timeout) 
            except ConnectionRefusedError:
                return Port(port, PortStatus.CONN_REFUSED)
            else:
                return Port(port, PortStatus.OPEN)

    def scan_ports(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            try:
                for result in executor.map(self.scan_single_port, self.ports):
                    self.scan_results.ports.append(result)
                    self.notify(result)
            except KeyboardInterrupt:
                print("\n[-] Scan ended by user input")
