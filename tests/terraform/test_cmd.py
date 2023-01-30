import logging
import os
import re

import pytest

import pterratest.terraform as terraform

LOGGER = logging.getLogger(__name__)


def test_run_terraform_command(terraform_hello_world_example_dir):
    options = terraform.Options.with_default_retryable_errors(terraform_dir=terraform_hello_world_example_dir)
    output = terraform.run_terraform_command(options, "init")

    assert re.search(r"Terraform has been successfully initialized!", output)
