from abc import ABC, abstractmethod
from src.cli_args import CLIArgumentsParser
from src.types import PortStatus

class Output(ABC):
    def __init__(self, subject):
        subject.attach(self) 
        self.subject = subject

    @abstractmethod
    def update(self, port) -> None:
        pass


class AllPortsScreenOutput(Output):
    def __init__(self, subject):
        super().__init__(subject)
        print(f"[+] Starting scan on {self.subject.target}\n")

    def update(self, port) -> None:
        print(f"\t{port}")


class OpenPortsScreenOutput(Output):
    def __init__(self, subject):
        super().__init__(subject)
        print(f"[+] Starting scan on {self.subject.target}\n")

    def update(self, port) -> None:
        if port.status == PortStatus.OPEN:
            print(f"\t{port}")


class AllPortsFileOutput(Output):
    def __init__(self, subject):
        super().__init__(subject)
        self.output_filepath = subject.output_file
        self.output_file = open(subject.output_file, mode="w", encoding="utf-8")
        self.output_file.write(f"[+] Results of scan on {self.subject.target}\n\n")

    def update(self, port) -> None:
        self.output_file.write(f"\t{str(port)}\n")
        if len(self.subject.scan_results.ports) == len(self.subject.ports):
            self.output_file.close()
            print(f"\n[+] Scan results successfully written to {self.output_filepath}")


class OpenPortsFileOutput(Output):
    def __init__(self, subject):
        super().__init__(subject)
        self.output_filepath = subject.output_file
        self.output_file = open(subject.output_file, mode="w", encoding="utf-8")
        self.output_file.write(f"[+] Results of scan on {self.subject.target}\n\n")

    def update(self, port) -> None:
        if port.status == PortStatus.OPEN:
            self.output_file.write(f"\t{str(port)}\n")
        if len(self.subject.scan_results.ports) == len(self.subject.ports):
            self.output_file.close()
            print(f"\n[+] Scan results successfully written to {self.output_filepath}")
