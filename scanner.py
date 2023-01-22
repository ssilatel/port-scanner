#!/usr/bin/python3
from src.cli_args import CLIArgumentsParser
from src.tcp_scanner import TCPScanner
from src.output import ScreenOutput, FileOutput

class App:
    def __init__(self):
        self.cli_args = CLIArgumentsParser().parse()
        self.tcp_scanner = TCPScanner(
                    target=self.cli_args.target,
                    ports=self.cli_args.ports,
                    timeout=self.cli_args.timeout,
                    output_file=self.cli_args.output,
                    threads=self.cli_args.max_threads
                )
        self.screen_output = ScreenOutput(self.tcp_scanner)
        if self.cli_args.output:
            self.file_output = FileOutput(self.tcp_scanner)

    def run(self):
        try:
            self.tcp_scanner.scan_ports()
        except KeyboardInterrupt:
            print("\n[-] Scan ended by user input")


if __name__ == "__main__":
    App().run()
