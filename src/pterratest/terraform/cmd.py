import subprocess
import shlex
import dataclasses
from typing import List, Callable

from pterratest.terraform.options import Options

from pterratest.retry import do_with_retryable_errors


def _generate_command(options: Options, *args: str) -> Callable[[], str]:
    def _cmd() -> str:
        p = subprocess.run(
            [options.terraform_binary] + list(args),
            cwd=options.terraform_dir,
            env=options.env_vars,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            text=True,
        )
        p.check_returncode()
        return p.stdout
    return _cmd


def run_terraform_command(options: Options, *args: str) -> str:
    cmd = _generate_command(options, *args)
    description = f"{options.terraform_binary} {args}"
    return do_with_retryable_errors(description, options.retryable_terraform_errors, options.max_retries, options.time_between_retries, cmd)

