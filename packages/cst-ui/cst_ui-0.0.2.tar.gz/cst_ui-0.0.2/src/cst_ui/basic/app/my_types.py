from dataclasses import dataclass
from typing import Union
import contextlib
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional
from asyncio import sleep
from typing import Callable
from flet import Page

with contextlib.suppress(ImportError):
    from jwt import decode, encode

from re import Pattern, compile
from typing import Callable, Dict, Optional, Tuple


@dataclass
class Msg:
    method: str
    key: str = None
    value: Union[str, dict] = None


@dataclass
class Redirect:
    route: str = None


TYPE_PATTERNS: Dict[str, Tuple[Pattern[str], Callable[[str], Optional[bool]]]] = {
    "int": (compile(r"-?\d+"), int),
    "float": (compile(r"-?\d+\.\d+"), float),
    "str": (compile(r"[^/]+"), str),
    "bool": (compile(r"(true|True|false|False)"), lambda x: x in ["true", "True"]),
}


@dataclass
class EncryptAlgorithm:
    HS256 = "HS256"
    RS256 = "RS256"


@dataclass
class PemKey:
    private: str
    public: str


@dataclass
class SecretKey:
    """Correctly add the secret key in the `FletApp` class parameter."""

    algorithm: str = "HS256"
    secret: str | None = None
    pem_key: PemKey | None = None
    Jwt: bool = False


def _time_exp(time_expiry: timezone, payload: Dict[str, Any]) -> Dict[str, Any]:
    if time_expiry is not None:
        payload["exp"] = datetime.now(tz=timezone.utc) + time_expiry
    return payload


def encode_RS256(payload: Dict[str, Any], private: str, time_expiry: timezone = None) -> str:
    payload = _time_exp(time_expiry, payload)
    return encode(
        payload=payload,
        key=private,
        algorithm="RS256",
    )


def encode_HS256(payload: Dict[str, Any], secret_key: str, time_expiry: timezone = None) -> str:
    payload = _time_exp(time_expiry, payload)
    return encode(
        payload=payload,
        key=secret_key,
        algorithm="HS256",
    )


def encode_verified(secret_key: SecretKey, value: str, time_expiration) -> Optional[str]:
    """Verify the possible encryption of the value sent."""
    assert (
        secret_key.algorithm is not None
    ), "The secret_key algorithm is not supported, only (RS256, HS256) is accepted."

    if secret_key.algorithm == "RS256":
        return encode_RS256(
            payload=value,
            private=secret_key.pem_key.private,
            time_expiry=time_expiration,
        )
    elif secret_key.algorithm == "HS256":
        return encode_HS256(
            payload=value,
            secret_key=secret_key.secret,
            time_expiry=time_expiration,
        )
    else:
        Exception("Algorithm not implemented in encode_verified method.")


async def _decode_payload_async(page: Page, key_login: str, secret_key: str, algorithms: str) -> Dict[str, Any]:
    """Decodes the payload stored in the client storage."""
    assert secret_key is not None, "The secret_key algorithm is not supported, only (RS256, HS256) is accepted."

    return decode(
        jwt=await page.client_storage.get_async(key_login),
        key=secret_key,
        algorithms=[algorithms],
    )


class Job:
    """Create time-definite tasks"""

    def __init__(
        self,
        func: Callable,
        key: str,
        every: timedelta,
        page: Page,
        login_done: bool,
        sleep_time: int = 1,
    ):
        self.func = func
        self.key = key
        self.every = every
        self.sleep_time = sleep_time
        self.task_running = False
        self.page = page
        self.login_done = login_done
        self.next_run_time = datetime.now() + self.every

    async def task(self):
        while self.task_running:
            await sleep(self.sleep_time)
            self.func()

    def start(self):
        if not self.task_running:
            self.task_running = True
            self.page.run_task(self.run_task)

    async def run_task(self):
        while datetime.now() <= self.next_run_time and self.login_done():
            await sleep(self.sleep_time)
        if self.login_done():
            self.func(self.key)()

    def stop(self):
        self.task_running = False
