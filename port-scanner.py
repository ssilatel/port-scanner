#!/usr/bin/python3
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
            help="Specify ports (separated by a comma if multiple)"
        )
        self.group.add_argument(
            "-f", "--file",
            type=argparse.FileType("r"),
            help="Specify file containing ports (ports must be separated by a "
                 "new line character '\\n', one port per line)",
        )

        args = self.parser.parse_args(*args, **kwargs)
        if args.all:
            self.ports = tuple(range(1, 65536))
        elif args.ports:
            self.parse_ports(args.ports)
        elif args.file:
            self.read_from_file(args.file)

        return {"target": args.target, "ports": self.ports}

    def read_from_file(self, file):
        with file as f:
            for line in file:
                line = line.strip()
                self.ports.append(int(line))

    def parse_ports(self, ports):
        if "," in ports:
            self.ports = ports.split(",")
            self.ports = [ int(p) for p in self.ports ]
        else:
            self.ports.append(int(ports))


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


if __name__ == "__main__":
    cli_args = CLIArgumentsParser().parse()

    PortScanner(
        target=cli_args["target"],
        ports=cli_args["ports"],
    ).scan_ports()
