import pytest

from pterratest import terraform


def test_terraform_hello_world_example(terraform_hello_world_example_dir_temp):
    options = terraform.Options.with_default_retryable_errors(terraform_dir=terraform_hello_world_example_dir_temp)

    with terraform.destroy(options):
        terraform.init_and_apply(options)
        output = terraform.output(options, "hello_world")
        assert output == "Hello, World!"
