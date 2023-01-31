from contextlib import contextmanager

from .cmd import run_terraform_command
from .options import Options


@contextmanager
def destroy(options: Options):
    yield
    args = ["destroy", "-auto-approve", "-input=false"]
    run_terraform_command(options, *args)
