import platform
from .cli import run_cli


def main():
    if platform.system() != "Linux" or platform.machine() != "aarch64":
        print("Error: This tool only supports Linux systems running on aarch64 (ARM64) architecture.")
        return
    run_cli()