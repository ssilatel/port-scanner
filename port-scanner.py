#!/usr/bin/python3
from collections.abc import Collection, Iterator
from dataclasses import dataclass
from enum import Enum
from typing import List
import argparse
import socket


class CLIArgumentsParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="Scan any number of ports on a target machine",
        )
        self.group = self.parser.add_mutually_exclusive_group()
        self.ports = tuple()
        self.args = None

    def parse(self, *args, **kwargs) -> argparse.Namespace:
        self.parser.add_argument("target", type=str, help="Target machine to scan")
        self.group.add_argument(
            "-a", "--all", help="Scan all ports", action="store_true"
        )
        self.group.add_argument(
            "-p",
            "--ports",
            type=str,
            help="Specify ports (separated by a comma if multiple, or a range "
            'of ports separated by a dash "-")',
        )
        self.group.add_argument(
            "-f",
            "--file",
            type=str,
            help="Specify file containing ports (ports must be separated by a "
            "new line character '\\n', one port per line)",
        )
        self.parser.add_argument(
            "-t",
            "--timeout",
            type=float,
            help="Set socket timeout",
            default=3.0
        )

        self.args = self.parser.parse_args(*args, **kwargs)

        if self.args.file:
            ports = self.read_from_file()
        else:
            ports = self.parse_ports()

        self.args.ports = tuple(ports)

        return self.args

    def read_from_file(self) -> Iterator[int]:
        try:
            with open(self.args.file, mode="r", encoding="utf_8") as f:
                yield from (int(line.strip()) for line in f)
        except FileNotFoundError:
            raise SystemExit(f"Error reading from file {self.args.file}")

    def parse_ports(self) -> Iterator[int]:
        if self.args.all is True:
            yield from range(1, 65536)
        else:
            for port in self.args.ports.split(","):
                if "-" in port:
                    start_port, end_port = port.split("-")
                    yield from range(int(start_port), int(end_port) + 1)
                else:
                    yield int(port)


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
        self.port_states = []

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
                    self.port_states.append(Port(p, PortStatus.TIMEOUT))
                    yield Port(p, PortStatus.TIMEOUT)
                except ConnectionRefusedError:
                    self.port_states.append(Port(p, PortStatus.CONN_REFUSED))
                    yield Port(p, PortStatus.CONN_REFUSED)
                else:
                    self.port_states.append(Port(p, PortStatus.OPEN))
                    yield Port(p, PortStatus.OPEN)

        self.scan_results = ScanResults(self.port_states)


class App:
    def __init__(self, port_scanner):
        self.port_scanner = port_scanner

    def scan(self):
        print(f"Starting scan on {self.port_scanner.target}\n")
        for port in self.port_scanner.scan_ports():
            print(port)


if __name__ == "__main__":
    cli_args = CLIArgumentsParser().parse()

    port_scanner = PortScanner(
        target=cli_args.target,
        ports=cli_args.ports,
        timeout=cli_args.timeout
    )

    app = App(port_scanner)
    app.scan()
