from typing import Union
from pyeitaa import raw

ChannelAdminLogEvent = Union[raw.types.ChannelAdminLogEvent]


# noinspection PyRedeclaration
class ChannelAdminLogEvent:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChannelAdminLogEvent <pyeitaa.raw.types.ChannelAdminLogEvent>`
    """

    QUALNAME = "pyeitaa.raw.base.ChannelAdminLogEvent"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
