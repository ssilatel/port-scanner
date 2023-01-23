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
            output_file: str,
            threads: int
        ):
        self.target = target
        self.ports = ports
        self.timeout = timeout
        self.output_file = output_file
        self.threads = threads
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
                return Port(port, PortStatus.TIMEOUT) 
            except ConnectionRefusedError:
                return Port(port, PortStatus.CONN_REFUSED)
            else:
                return Port(port, PortStatus.OPEN)

    def contains_open_ports(self):
        for p in self.scan_results.ports:
            if p.status == PortStatus.OPEN:
                return True
        return False

    def scan_ports(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            try:
                for result in executor.map(self.scan_single_port, self.ports):
                    self.scan_results.ports.append(result)
                    self.notify(result)
            except KeyboardInterrupt:
                print("\n[-] Scan ended by user input")

        if not self.contains_open_ports():
            print(f"[-] No open ports were found on {self.target}")
            if self.output_file:
                with open(self.output_file, mode="a", encoding="utf-8") as f:
                    f.write(f"[-] No open ports were found on {self.target}")
