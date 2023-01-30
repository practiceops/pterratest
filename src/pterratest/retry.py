import logging
from subprocess import CalledProcessError
import re
from typing import Callable, Dict

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
    logger: logging.Logger = _LOGGER,
) -> str:
    num_attempts = 0
    try:
        for attempt in tenacity.Retrying(
            retry=tenacity.retry_if_exception_type(RetryableError),
            stop=tenacity.stop_after_attempt(max_attempts),
            wait=tenacity.wait_fixed(sleep_between_retries),
        ):
            with attempt:
                logger.debug(f"attempting action: '{action_description}', attempt: {num_attempts}/{max_attempts}")
                num_attempts += 1
                return action()
    except tenacity.RetryError as e:
        if num_attempts == max_attempts:
            message = "'{action_description}' failed after {max_attempts} attempts"
            logger.critical(message)
            raise MaxRetriesExceeded(message) from e
        raise


def do_with_retryable_errors(
    action_description: str,
    retryable_errors: Dict[str, str],
    max_attempts: int,
    sleep_between_retries: int,
    action: Callable[[], str],
    *,
    logger: logging.Logger = _LOGGER,
) -> str:
    retryable_regexes = {re.compile(pattern): error_message for pattern, error_message in retryable_errors.items()}

    def _retryable_action():
        try:
            return action()
        except CalledProcessError as e:
            for pattern, error_message in retryable_regexes.items():
                if pattern.search(e.output) is not None:
                    message = f"'{action_description}' failed with error matching '{pattern}', but this error was expected and warrants a retry. Further details: '{error_message}'\n"
                    logger.critical(message)
                    raise RetryableError(message)
            raise FatalError(f"'{action_description}' failed with a fatal error, cmd='{e.cmd}', returncode='{e.returncode}', output={e.output}\n") from e

    return do_with_retry(action_description, max_attempts, sleep_between_retries, _retryable_action)
