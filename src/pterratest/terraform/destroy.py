from contextlib import contextmanager

from .cmd import run_terraform_command
from .options import Options


def destroy(options: Options) -> str:
    """Runs terraform destroy with the given options and return stdout/stderr."""
    args = ["destroy", "-auto-approve", "-input=false"]
    return run_terraform_command(options, *args)


@contextmanager
def defer_destroy(options: Options):
    """A context manager that runs terraform destroy on exit."""
    yield
    destroy(options)
