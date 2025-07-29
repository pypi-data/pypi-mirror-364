from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timezone
from getpass import getpass
from typing import Union, List, Dict, Optional
import asyncio
import functools

import pyeitaa
from pyeitaa import raw, enums
from pyeitaa import types


async def ainput(prompt: str = "", *, hide: bool = False, loop: Optional[asyncio.AbstractEventLoop] = None):
    """Just like the built-in input, but async"""
    if isinstance(loop, asyncio.AbstractEventLoop):
        loop = loop
    else:
        loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(1) as executor:
        func = functools.partial(getpass if hide else input, prompt)
        return await loop.run_in_executor(executor, func)


async def parse_text_entities(
    client: "pyeitaa.Client",
    text: str,
    parse_mode: Optional[enums.ParseMode],
    entities: Optional[List["types.MessageEntity"]]
) -> Dict[str, Union[str, List[raw.base.MessageEntity]]]:
    if entities:
        # Inject the client instance because parsing user mentions requires it
        for entity in entities:
            entity._client = client

        text, entities = text, [await entity.write() for entity in entities] or None
    else:
        text, entities = (await client.parser.parse(text, parse_mode)).values()

    return {
        "message": text,
        "entities": entities
    }


def zero_datetime() -> datetime:
    return datetime.fromtimestamp(0, timezone.utc)


def max_datetime() -> datetime:
    return datetime.fromtimestamp((1 << 31) - 1, timezone.utc)


def timestamp_to_datetime(ts: Optional[int]) -> Optional[datetime]:
    return datetime.fromtimestamp(ts) if ts else None


def datetime_to_timestamp(dt: Optional[datetime]) -> Optional[int]:
    return int(dt.timestamp()) if dt else None
