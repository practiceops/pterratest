# pylint: disable=redefined-outer-name
import os
import shutil

import pytest

from pterratest.test_structure import copy_terraform_folder_to_temp


@pytest.fixture
def test_dir() -> str:
    """Returns the path to the top-level tests dir."""
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def examples_dir(test_dir) -> str:
    """Returns the path to the top-level examples dir."""
    return os.path.abspath(os.path.join(test_dir, os.pardir, "examples"))


@pytest.fixture
def examples_dir_temp(examples_dir) -> str:
    """Returns a temp dir path to a copy of the examples dir."""
    temp_dir = copy_terraform_folder_to_temp(examples_dir)
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def terraform_hello_world_example_dir_temp(examples_dir_temp) -> str:
    """Returns a temp dir path to a copy of the `terraform_hello_world` example dir."""
    return os.path.join(examples_dir_temp, "terraform_hello_world")
