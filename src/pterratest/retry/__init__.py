import tenacity
import re
from typing import Dict, Callable


class RetryableError(Exception):
    """Raised when an error may be resolved by retrying."""


class MaxRetriesExceeded(Exception):
    """Raised when the maximum amount of retries is exceeded."""


def do_with_retry(action_description: str, max_retries: int, sleep_between_retries: int, action: Callable[[], str]) -> str:
    num_attempts = 0
    max_attempts = max_retries + 1
    try:
        for attempt in tenacity.Retrying(
            retry=tenacity.retry_if_exception_type(RetryableError),
            stop=tenacity.stop_after_attempt(max_attempts),
            wait=tenacity.wait_fixed(sleep_between_retries),
        ):
            with attempt:
                num_attempts += 1
                return action()
    except tenacity.RetryError as e:
        if num_attempts == max_attempts:
            raise MaxRetriesExceeded(f"'{action_description}' failed after {max_attempts} attempts") from e
        raise


def do_with_retryable_errors(
    action_description: str,
    retryable_errors: Dict[str, str],
    max_retries: int,
    sleep_between_retries: int,
    action: Callable[[], str],
) -> str:
    retryable_regexes = {re.compile(pattern):error_message for pattern, error_message in retryable_errors.items()}

    def retryable_action():
        try:
            return action()
        except Exception as e:
            for pattern, error_message in retryable_regexes.items():
                if pattern.search(str(e)) is not None:
                    message = f"'{action_description}' failed with the error '{str(e)}' but this error was expected and warrants a retry. Further details: '{error_message}'\n"
                    # TODO: log the message
                    raise RetryableError(message)

    return do_with_retry(action_description, max_retries, sleep_between_retries, action)

