import re
from datetime import datetime
from importlib import import_module
from typing import Type, Union

from pyeitaa import raw
from pyeitaa.raw.core import TLObject
from .exceptions.all import exceptions


class RPCError(Exception):
    ID = None
    CODE = None
    NAME = None
    MESSAGE = "{x}"

    def __init__(self, x: Union[int, raw.types.RpcError] = None, rpc_name: str = None, is_unknown: bool = False):
        super().__init__("[{} {}]: {} {}".format(
            self.CODE,
            self.ID or self.NAME,
            self.MESSAGE.format(x=x),
            f'(caused by "{rpc_name}")' if rpc_name else ""
        ))

        try:
            self.x = int(x)
        except (ValueError, TypeError):
            self.x = x

        if is_unknown:
            with open("unknown_errors.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()}\t{x}\t{rpc_name}\n")

    @staticmethod
    def raise_it(rpc_error: "raw.types.RpcError", rpc_type: Type[TLObject]):
        error_code = rpc_error.error_code
        error_message = rpc_error.error_message
        rpc_name = ".".join(rpc_type.QUALNAME.split(".")[1:])

        if error_code not in exceptions:
            raise UnknownError(
                x=f"[{error_code} {error_message}]",
                rpc_name=rpc_name,
                is_unknown=True
            )

        error_id = re.sub(r"_\d+", "_X", error_message)

        if error_id not in exceptions[error_code]:
            raise getattr(
                import_module("pyeitaa.errors"),
                exceptions[error_code]["_"]
            )(x=f"[{error_code} {error_message}]",
              rpc_name=rpc_name,
              is_unknown=True)

        x = re.search(r"_(\d+)", error_message)
        x = x.group(1) if x is not None else x

        raise getattr(
            import_module("pyeitaa.errors"),
            exceptions[error_code][error_id]
        )(x=x,
          rpc_name=rpc_name,
          is_unknown=False)


class UnknownError(RPCError):
    CODE = 520
    """:obj:`int`: Error code"""
    NAME = "Unknown error"
