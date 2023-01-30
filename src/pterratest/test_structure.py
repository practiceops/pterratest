import tempfile
import os
import logging
import shutil
from typing import List

_LOGGER = logging.getLogger(__name__)


_COPY_TERRAFORM_FOLDER_IGNORE_PATTERNS = [
    ".terraform*",
    "*.tfstate",
    "*.tfstate.backup",
    "*.tfvars",
    "*.tfvars.json",
]


def copy_terraform_folder_to_dest(root_folder: str, terraform_module_folder: str, dest_root_folder: str, *, ignore_patterns: List[str] = _COPY_TERRAFORM_FOLDER_IGNORE_PATTERNS, logger: logging.Logger = _LOGGER) -> str:
    """Copies the given root folder to a new root folder and returns the path to the given terraform modules folder within the new root folder.

    Ignores terraform files such as tfstate and tfvars.
    """
    logger.debug(f"copying terraform folder '{root_folder}' to '{dest_root_folder}'")
    shutil.copytree(
        root_folder,
        dest_root_folder,
        ignore=shutil.ignore_patterns(*ignore_patterns),
        dirs_exist_ok=True,
    )
    return os.path.join(dest_root_folder, terraform_module_folder)


def copy_terraform_folder_to_temp(root_folder: str, terraform_module_folder: str = "") -> str:
    """Copies the given root folder to a new temporary root folder and returns the path to the given terraform modules folder within the new root folder."""
    return copy_terraform_folder_to_dest(root_folder, terraform_module_folder, tempfile.mkdtemp())

