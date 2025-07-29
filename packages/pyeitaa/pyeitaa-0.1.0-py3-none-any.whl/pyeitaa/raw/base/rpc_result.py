from typing import Union
from pyeitaa import raw

RpcResult = Union[raw.types.RpcResult, raw.types.RpcResult]


# noinspection PyRedeclaration
class RpcResult:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`RpcResult <pyeitaa.raw.types.RpcResult>`
            - :obj:`RpcResult <pyeitaa.raw.types.RpcResult>`
    """

    QUALNAME = "pyeitaa.raw.base.RpcResult"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
