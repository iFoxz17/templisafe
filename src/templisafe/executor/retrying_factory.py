import logging
from typing import Any, Callable

from tenacity import (
    RetryCallState,
    Retrying,
    retry_any,
    retry_base,
    retry_if_exception_type,
    retry_if_result,
    retry_never,
    stop_after_attempt,
    stop_after_delay,
    stop_any,
    stop_never,
    wait_chain,
    wait_exponential,
    wait_fixed,
    wait_none,
    wait_random,
)
from tenacity.stop import stop_base
from tenacity.wait import wait_base

from templisafe.settings.source_executor_settings import (
    RetryConditionSettings,
    StopSettings,
    TenacitySettings,
    WaitSettings,
)

logger = logging.getLogger("templisafe.retry")
logger.setLevel(logging.INFO)


def log_retry_attempt(retry_state: RetryCallState) -> None:
    if retry_state.outcome is None:
        return

    func_name: str = retry_state.fn.__name__ if retry_state.fn else "_unknown_"
    idle_for: float = retry_state.idle_for
    retry_msg: str = f" Retrying in {idle_for} s" if idle_for else ""
    exc: BaseException | None = retry_state.outcome.exception()

    msg: str
    log_fun: Callable
    if exc is not None:
        logger.warning(
            "Attempt #%d failed for function '%s' with exception: %s." + retry_msg,
            retry_state.attempt_number,
            func_name,
            exc,
        )
    else:
        result = retry_state.outcome.result()
        logger.info(
            "Attempt #%d for function '%s' returned result triggering retry: %s." + retry_msg,
            retry_state.attempt_number,
            func_name,
            result,
        )


class RetryingFactory:
    """
    Creates Tenacity `Retrying` objects from declarative settings.

    For each part of the policy (stop, wait, retry), the factory instantiates the
    corresponding Tenacity strategy only if at least one of the relevant fields
    is not `None`. Any other field of the specific policy strategy left as `None`
    is filled with Tenacity library defaults.

    When more than one strategy applies to a given part of the policy, the factory merges
    them into a composite strategy that respects all configured behaviors.
    """

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def _build_stop(self, stop_policy: StopSettings) -> stop_base:
        stops: list[stop_base] = []

        if stop_policy.max_attempts is not None:
            stops.append(stop_after_attempt(stop_policy.max_attempts))

        if stop_policy.max_delay_seconds is not None:
            stops.append(stop_after_delay(stop_policy.max_delay_seconds))

        if not stops:
            return stop_never

        return stop_any(*stops)

    def _build_wait(self, wait_policy: WaitSettings) -> wait_base:
        waits: list[wait_base] = []
        if wait_policy.fixed_seconds is not None:
            waits.append(wait_fixed(wait_policy.fixed_seconds))

        exp_kwargs: dict[str, Any] = {
            k: v
            for k, v in zip(
                ("multiplier", "exp_base", "min", "max"),
                (
                    wait_policy.multiplier_seconds,
                    wait_policy.exponential_base,
                    wait_policy.min_seconds,
                    wait_policy.max_seconds,
                ),
            )
            if v is not None
        }
        if exp_kwargs:
            waits.append(wait_exponential(**exp_kwargs))

        if wait_policy.jitter is not None:
            waits.append(wait_random(0, wait_policy.jitter))

        if not waits:
            return wait_none()

        return wait_chain(*waits)

    def _build_retry_condition(self, retry_policy: RetryConditionSettings) -> retry_base:
        retries: list[retry_base] = []

        retries.append(retry_if_exception_type(Exception))

        if retry_policy.retry_if_result_none:
            retries.append(retry_if_result(lambda result: not isinstance(result, str)))

        if not retries:
            return retry_never

        return retry_any(*retries)

    def create(self, policy: TenacitySettings) -> Retrying:
        """
        Create a fully configured Tenacity `Retrying` instance from the `TenacitySettings`.

        Parameters
        ----------
        policy : TenacitySettings
            Declarative settings defining stop, wait and retry behavior.

        Returns
        -------
        Retrying
            A Tenacity `Retrying` object ready to execute functions with the
            specified resilience policy.
        """

        return Retrying(
            stop=self._build_stop(policy.stop),
            wait=self._build_wait(policy.wait),
            retry=self._build_retry_condition(policy.retry_conditions),
            reraise=policy.reraise,
            before_sleep=log_retry_attempt,
        )
