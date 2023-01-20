#!/usr/bin/python3
from cli_args import CLIArgumentsParser
from port_scanner import PortScanner

class App:
    def __init__(self):
        self.cli_args = CLIArgumentsParser().parse()
        self.port_scanner = PortScanner(
                    target=self.cli_args.target,
                    ports=self.cli_args.ports,
                    timeout=self.cli_args.timeout
                )

    def scan(self):
        print(f"Starting scan on {self.port_scanner.target}\n")
        for port in self.port_scanner.scan_ports():
            print(port)


if __name__ == "__main__":
    App().scan()
