from typing import Union
from pyeitaa import raw

Pong = Union[raw.types.Pong, raw.types.Pong]


# noinspection PyRedeclaration
class Pong:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Pong <pyeitaa.raw.types.Pong>`
            - :obj:`Pong <pyeitaa.raw.types.Pong>`

    See Also:
        This object can be returned by 4 methods:

        .. hlist::
            :columns: 2

            - :obj:`Ping <pyeitaa.raw.functions.Ping>`
            - :obj:`PingDelayDisconnect <pyeitaa.raw.functions.PingDelayDisconnect>`
            - :obj:`Ping <pyeitaa.raw.functions.Ping>`
            - :obj:`PingDelayDisconnect <pyeitaa.raw.functions.PingDelayDisconnect>`
    """

    QUALNAME = "pyeitaa.raw.base.Pong"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
