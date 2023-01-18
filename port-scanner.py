#!/usr/bin/python3
import argparse
import socket
from collections.abc import Iterator


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
        self.parser.add_argument(
            "target",
            type=str,
            help="Target machine to scan"
        )
        self.group.add_argument(
            "-a", "--all",
            help="Scan all ports",
            action="store_true"
        )
        self.group.add_argument(
            "-p", "--ports",
            type=str,
            help="Specify ports (separated by a comma if multiple, or a range "
                 "of ports separated by a dash \"-\")"
        )
        self.group.add_argument(
            "-f", "--file",
            type=str,
            help="Specify file containing ports (ports must be separated by a "
                 "new line character '\\n', one port per line)"
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
            if "-" in self.args.ports:
                port_range = self.args.ports.split("-")
                yield from range(int(port_range[0]), int(port_range[1]) + 1)
            else:
                yield from (int(port) for port in self.args.ports.split(","))


class PortScanner:
    def __init__(self, target: str, ports):
        self.target = target
        self.ports = ports

    def scan_ports(self):
        print("Starting scan...\n")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        open_ports = []
        for p in self.ports:
            result = sock.connect_ex((self.target, p))
            if result == 0:
                open_ports.append(p)
        if len(open_ports) > 0:
            for p in open_ports:
                print(f"Port {p} on {self.target} is open")
        else:
            print(f"None of the specified ports are open on {self.target}")
        sock.close()


if __name__ == "__main__":
    cli_args = CLIArgumentsParser().parse()

    PortScanner(
        target=cli_args.target,
        ports=cli_args.ports,
    ).scan_ports()
