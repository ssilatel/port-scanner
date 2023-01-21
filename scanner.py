#!/usr/bin/python3
from src.cli_args import CLIArgumentsParser
from src.scanner_core import PortScanner
from src.output import ScreenOutput, FileOutput

class App:
    def __init__(self):
        self.cli_args = CLIArgumentsParser().parse()
        self.port_scanner = PortScanner(
                    target=self.cli_args.target,
                    ports=self.cli_args.ports,
                    timeout=self.cli_args.timeout,
                    output_file=self.cli_args.output
                )
        self.screen_output = ScreenOutput(self.port_scanner)
        if self.cli_args.output:
            self.file_output = FileOutput(self.port_scanner)

    def run(self):
        self.port_scanner.scan_ports()


if __name__ == "__main__":
    App().run()
