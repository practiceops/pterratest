import logging
import subprocess
from typing import Callable

from pterratest.retry import do_with_retryable_errors

from .options import Options

_LOGGER = logging.getLogger(__name__)


def _generate_command(options: Options, *args: str) -> Callable[[], str]:
    def _cmd() -> str:
        p = subprocess.run(
            [options.terraform_binary] + list(args),
            cwd=options.terraform_dir,
            env=options.env_vars,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            check=True,
            text=True,
        )
        return p.stdout

    return _cmd


def run_terraform_command(options: Options, *args: str) -> str:
    """Runs terraform with the given arguments and options and return stdout/stderr."""
    cmd = _generate_command(options, *args)
    action_description = " ".join([options.terraform_binary] + list(args))
    return do_with_retryable_errors(
        action_description,
        options.retryable_terraform_errors,
        options.max_retries,
        options.time_between_retries,
        cmd,
    )
