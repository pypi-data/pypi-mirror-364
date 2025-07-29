import os
import subprocess
import argparse

def run_cli():
    parser = argparse.ArgumentParser(description="ipg-cli tool")
    parser.add_argument("-r", "--run", required=False, help="Run a command")
    parser.add_argument("-v", "--version", action="store_true", help="Display version")

    args = parser.parse_args()
    if(args.run):
        subprocess.run(args.run, shell=True)
    if(args.version):
        print(os.environ["IPG_CLI_VERSION"])
