import asyncio
import base64
import functools
import random
import socket
from typing import Awaitable, Set
from uuid import UUID

import async_timeout
from pyhap.json_adapter import dumps, loads, OPT_SORT_KEYS

from .const import BASE_UUID

ALPHANUM = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
HEX_DIGITS = "0123456789ABCDEF"
_BACKGROUND_TASKS: Set[asyncio.Task] = set()


rand = random.SystemRandom()


def callback(func):
    """Decorator for non blocking functions."""
    setattr(func, "_pyhap_callback", True)
    return func


def is_callback(func):
    """Check if function is callback."""
    return "_pyhap_callback" in getattr(func, "__dict__", {})


def iscoro(func):
    """Check if the function is a coroutine or if the function is a ``functools.partial``,
    check the wrapped function for the same.
    """
    if isinstance(func, functools.partial):
        func = func.func
    return asyncio.iscoroutinefunction(func)


def get_local_address() -> str:
    """
    Grabs the local IP address using a socket.

    :return: Local IP Address in IPv4 format.
    :rtype: str
    """
    # TODO: try not to talk 8888 for this
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        addr = s.getsockname()[0]
    finally:
        s.close()
    return str(addr)


def long_to_bytes(n):
    """
    Convert a ``long int`` to ``bytes``

    :param n: Long Integer
    :type n: int

    :return: ``long int`` in ``bytes`` format.
    :rtype: bytes
    """
    byteList = []
    x = 0
    off = 0
    while x != n:
        b = (n >> off) & 0xFF
        byteList.append(b)
        x = x | (b << off)
        off += 8
    byteList.reverse()
    return bytes(byteList)


def generate_mac():
    """
    Generates a fake mac address used in broadcast.

    :return: MAC address in format XX:XX:XX:XX:XX:XX
    :rtype: str
    """
    return "{}{}:{}{}:{}{}:{}{}:{}{}:{}{}".format(  # pylint: disable=consider-using-f-string
        *(rand.choice(HEX_DIGITS) for _ in range(12))
    )


def generate_setup_id():
    """
    Generates a random Setup ID for an ``Accessory`` or ``Bridge``.

    Used in QR codes and the setup hash.

    :return: 4 digit alphanumeric code.
    :rtype: str
    """
    return "".join([rand.choice(ALPHANUM) for i in range(4)])


def generate_pincode():
    """
    Generates a random pincode.

    :return: pincode in format ``xxx-xx-xxx``
    :rtype: bytearray
    """
    return "{}{}{}-{}{}-{}{}{}".format(  # pylint: disable=consider-using-f-string
        *(rand.randint(0, 9) for i in range(8))
    ).encode("ascii")


def to_base64_str(bytes_input) -> str:
    return base64.b64encode(bytes_input).decode("utf-8")


def base64_to_bytes(str_input) -> bytes:
    return base64.b64decode(str_input.encode("utf-8"))


def byte_bool(boolv):
    return b"\x01" if boolv else b"\x00"


async def event_wait(event, timeout):
    """Wait for the given event to be set or for the timeout to expire.

    :param event: The event to wait for.
    :type event: asyncio.Event

    :param timeout: The timeout for which to wait, in seconds.
    :type timeout: float

    :return: ``event.is_set()``
    :rtype: bool
    """
    try:
        async with async_timeout.timeout(timeout):
            await event.wait()
    except asyncio.TimeoutError:
        pass
    return event.is_set()


@functools.lru_cache(maxsize=2048)
def uuid_to_hap_type(uuid: UUID) -> str:
    """Convert a UUID to a HAP type."""
    long_type = str(uuid).upper()
    if not long_type.endswith(BASE_UUID):
        return long_type
    return long_type.split("-", 1)[0].lstrip("0")


@functools.lru_cache(maxsize=2048)
def hap_type_to_uuid(hap_type):
    """Convert a HAP type to a UUID."""
    if "-" in hap_type:
        return UUID(hap_type)
    return UUID("0" * (8 - len(hap_type)) + hap_type + BASE_UUID)


def to_hap_json(dump_obj):
    """Convert an object to HAP json."""
    return dumps(dump_obj)


def to_sorted_hap_json(dump_obj):
    """Convert an object to sorted HAP json."""
    return dumps(dump_obj, option=OPT_SORT_KEYS)


def from_hap_json(json_str):
    """Convert json to an object."""
    return loads(json_str)


def async_create_background_task(func: Awaitable) -> asyncio.Task:
    """Create a background task and add it to the set of background tasks."""
    task = asyncio.ensure_future(func)
    _BACKGROUND_TASKS.add(task)
    task.add_done_callback(_BACKGROUND_TASKS.discard)
    return task
