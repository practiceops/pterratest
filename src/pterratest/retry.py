import logging
import re
from subprocess import CalledProcessError
from typing import Callable, Dict, Optional

import tenacity

_LOGGER = logging.getLogger(__name__)


class RetryableError(Exception):
    """Raised when an error may be resolved by retrying."""


class FatalError(Exception):
    """Raised when an error should not be retried."""


class MaxRetriesExceeded(Exception):
    """Raised when the maximum amount of retries is exceeded."""


def do_with_retry(
    action_description: str,
    max_attempts: int,
    sleep_between_retries: int,
    action: Callable[[], str],
    *,
    logger: Optional[logging.Logger] = None,
) -> str:
    """Runs the specified action. If it returns a string, return that string.

    If it returns a FatalError, return that error immediately.
    If it returns any other type of error, sleep for sleep_between_retries and try again, up to a maximum of
    max_attempt attempts. If max_attempts is exceeded, fail with MaxRetriesExceeded.
    """
    if logger is None:
        logger = _LOGGER

    num_attempts = 1
    for attempt in tenacity.Retrying(
        retry=tenacity.retry_if_not_exception_type(FatalError),
        stop=tenacity.stop_after_attempt(max_attempts),
        wait=tenacity.wait_fixed(sleep_between_retries),
        reraise=True,
    ):
        logger.debug(f"attempting action: '{action_description}', attempt: {num_attempts}/{max_attempts}")
        with attempt:
            return action()
        num_attempts += 1

    message = f"'{action_description}' failed after {max_attempts} attempts"
    logger.critical(message)
    raise MaxRetriesExceeded(message)


def do_with_retryable_errors(
    action_description: str,
    retryable_errors: Dict[str, str],
    max_attempts: int,
    sleep_between_retries: int,
    action: Callable[[], str],
    *,
    logger: Optional[logging.Logger] = None,
) -> str:
    """Runs the specified action. If it returns a string, return that string.

    If it returns an error, check if the error message or the string output from the action (which is often
    stdout/stderr from running some command) matches any of the regular expressions in the specified retryable_errors
    dict. If there is a match, sleep for sleep_between_retries, and retry the specified action, up to a maximum of
    max_attempts attempts. If there is no match, return that error immediately, wrapped in a FatalError.
    If max_retries is exceeded, fail with MaxRetriesExceeded.
    """
    if logger is None:
        logger = _LOGGER

    retryable_regexes = {re.compile(pattern): error_message for pattern, error_message in retryable_errors.items()}

    def _retryable_action():
        try:
            return action()
        except CalledProcessError as e:
            for pattern, error_message in retryable_regexes.items():
                if pattern.search(e.output) is not None:
                    message = (
                        f"'{action_description}' failed with error matching '{pattern}', but this error was expected"
                        f" and warrants a retry. Further details: '{error_message}'\n"
                    )
                    logger.critical(message)
                    raise RetryableError(message) from e
            raise FatalError(
                f"'{action_description}' failed with a fatal error, cmd='{e.cmd}',"
                f" returncode='{e.returncode}', output={e.output}\n"
            ) from e

    return do_with_retry(action_description, max_attempts, sleep_between_retries, _retryable_action)
