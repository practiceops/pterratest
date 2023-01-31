import json
from typing import Optional

from .cmd import run_terraform_command
from .options import Options


def output_json(options: Options, key: Optional[str] = None) -> str:
    args = ["output", "-no-color", "-json"]
    if key is not None:
        args.append(key)
    return run_terraform_command(options, *args)


def output(options: Options, key: str) -> Optional[str]:
    """Calls terraform output for the given variable and return its string value representation.

    It only designed to work with primitive terraform types: string, number and bool.

    Returns None if the key does not exist.
    """
    return json.loads(output_json(options)).get(key, {}).get("value")
