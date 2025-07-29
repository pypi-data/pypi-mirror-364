from typing import Union
from pyeitaa import raw

ServerDHParams = Union[raw.types.ServerDHParamsFail, raw.types.ServerDHParamsOk, raw.types.ServerDHParamsOk]


# noinspection PyRedeclaration
class ServerDHParams:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ServerDHParamsFail <pyeitaa.raw.types.ServerDHParamsFail>`
            - :obj:`ServerDHParamsOk <pyeitaa.raw.types.ServerDHParamsOk>`
            - :obj:`ServerDHParamsOk <pyeitaa.raw.types.ServerDHParamsOk>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`ReqDHParams <pyeitaa.raw.functions.ReqDHParams>`
            - :obj:`ReqDHParams <pyeitaa.raw.functions.ReqDHParams>`
    """

    QUALNAME = "pyeitaa.raw.base.ServerDHParams"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
