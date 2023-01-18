#!/usr/bin/python3
import argparse
import socket
from collections.abc import Collection, Iterator


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


class PortScanner:
    def __init__(self, target: str, ports: Collection[int]):
        self.target = target
        self.ports = ports
        self.open_ports = []

    def scan_ports(self):
        print(f"Starting scan on {self.target}...\n")
        for p in self.ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    sock.settimeout(3)
                    sock.connect((self.target, p))
                    self.open_ports.append(p)
                except socket.gaierror:
                    raise SystemExit(
                        f"Failed to connect or resolve hostname to target "
                        f"address {self.target}"
                    )
                except socket.timeout:
                    print(f"Port {p} is closed or timed out")
                except ConnectionRefusedError:
                    print(f"Port {p} is closed or the server refused to connect")
                else:
                    print(f"Port {p} is open")


if __name__ == "__main__":
    cli_args = CLIArgumentsParser().parse()

    PortScanner(
        target=cli_args.target,
        ports=cli_args.ports,
    ).scan_ports()
