import os
import shutil
from dataclasses import dataclass, field, replace
from typing import Dict, Optional

_DEFAULT_RETRYABLE_TERRAFORM_ERRORS: Dict[str, str] = {
    # Helm related terraform calls may fail when too many tests run in parallel. While the exact cause is unknown,
    # this is presumably due to all the network contention involved. Usually a retry resolves the issue.
    r".*read: connection reset by peer.*": "Failed to reach helm charts repository.",
    r".*transport is closing.*": "Failed to reach Kubernetes API.",
    # `terraform init` frequently fails in CI due to network issues accessing plugins. The reason is unknown, but
    # eventually these succeed after a few retries.
    r".*unable to verify signature.*": "Failed to retrieve plugin due to transient network error.",
    r".*unable to verify checksum.*": "Failed to retrieve plugin due to transient network error.",
    r".*no provider exists with the given name.*": "Failed to retrieve plugin due to transient network error.",
    r".*registry service is unreachable.*": "Failed to retrieve plugin due to transient network error.",
    r".*Error installing provider.*": "Failed to retrieve plugin due to transient network error.",
    r".*Failed to query available provider packages.*": "Failed to retrieve plugin due to transient network error.",
    r".*timeout while waiting for plugin to start.*": "Failed to retrieve plugin due to transient network error.",
    r".*timed out waiting for server handshake.*": "Failed to retrieve plugin due to transient network error.",
    r"could not query provider registry for": "Failed to retrieve plugin due to transient network error.",
    # Provider bugs where the data after apply is not propagated. This is usually an eventual consistency issue, so
    # retrying should self resolve it.
    # See https://github.com/terraform-providers/terraform-provider-aws/issues/12449 for an example.
    r".*Provider produced inconsistent result after apply.*": "Provider eventual consistency error.",
}

_TERRAFORM_PATH = shutil.which("terraform")


@dataclass
class Options:
    """Options for running terraform commands."""

    terraform_binary: str = _TERRAFORM_PATH
    terraform_dir: str = field(default_factory=os.getcwd)

    vars: Dict[str, str] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)
    retryable_terraform_errors: Dict[str, str] = field(default_factory=dict)
    max_retries: int = 3
    time_between_retries: int = 5

    @classmethod
    def with_default_retryable_errors(cls, *args, **kwargs) -> "Options":
        """This functions returns an Options object with sensible defaults for retryable errors."""
        return _with_default_retryable_errors(cls(*args, **kwargs))


def _with_default_retryable_errors(
    original_options: Options, retryable_terraform_errors: Optional[Dict[str, str]] = None
) -> Options:
    """This functions makes a copy of the Options object and returns an updated object with sensible defaults for
    retryable errors.
    """
    if retryable_terraform_errors is None:
        retryable_terraform_errors = _DEFAULT_RETRYABLE_TERRAFORM_ERRORS

    return replace(original_options, retryable_terraform_errors=retryable_terraform_errors)
