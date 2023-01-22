from collections.abc import Iterator
import argparse

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
            help="Set socket timeout (default=3.0)",
            default=3.0
        )
        self.parser.add_argument(
            "-o",
            "--output",
            type=str,
            help="Save the output to the specified filepath",
            default=""
        )
        self.parser.add_argument(
            "-m",
            "--max-threads",
            type=int,
            help="Specify number of threads (default=10)",
            default=10
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
