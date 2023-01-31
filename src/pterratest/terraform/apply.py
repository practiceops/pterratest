from .cmd import run_terraform_command
from .init import init
from .options import Options


def init_and_apply(options: Options) -> str:
    """Runs terraform init and apply with the given options and return stdout/stderr from the apply command.

    Note that this method does NOT call destroy and assumes the caller is
    responsible for cleaning up any resources created by running apply.
    """
    init(options)
    return apply(options)


def apply(options: Options) -> str:
    """Runs terraform apply with the given options and return stdout/stderr.

    Note that this method does NOT call destroy and assumes the caller is
    responsible for cleaning up any resources created by running apply.
    """
    args = ["apply", "-auto-approve", "-input=false"]
    return run_terraform_command(options, *args)
