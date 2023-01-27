# import pytest

# from pterratest import terraform


# def test_terraform_hello_world_example(terraform_hello_world_example_dir):
#     options = terraform.Options.with_default_retryable_errors(terraform_dir=terraform_hello_world_example_dir)
#
#     with terraform.destroy(opts):
#         terraform.init_and_apply(opts)
#         output = terraform.output(opts, "hello_world")
#         assert output == "Hello, World!"

