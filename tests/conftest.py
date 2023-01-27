import os

import pytest


@pytest.fixture
def test_dir() -> str:
    """Returns the path to the top-level tests dir."""
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def examples_dir(test_dir) -> str:
    """Returns the path to the top-level examples dir."""
    return os.path.join(test_dir, os.pardir, "examples")


@pytest.fixture
def terraform_hello_world_example_dir(examples_dir) -> str:
    """Returns the path to the `terraform_hello_world` example dir."""
    return os.path.join(examples_dir, "terraform_hello_world")
