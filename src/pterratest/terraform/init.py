from .cmd import run_terraform_command
from .options import Options


def init(options: Options) -> str:
    """Calls terraform init and retrurns stdout/stderr."""
    args = ["init"]
    return run_terraform_command(options, *args)
