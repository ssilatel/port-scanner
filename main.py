#!/usr/bin/python3
from cli_args import CLIArgumentsParser
from port_scanner import PortScanner

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
