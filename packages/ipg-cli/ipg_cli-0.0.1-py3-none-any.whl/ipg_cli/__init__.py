import os

__all__ = ["main.py"]
os.environ["IPG_CLI_VERSION"] = "0.0.1"
os.environ["IPG_CLI_DIR_PATH"] = os.path.dirname(os.path.abspath(__file__))
os.environ["IPG_CLI_DOCKER_VERSION"] = "1.1"

from .main import main
