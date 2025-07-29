from typing import Union
from pyeitaa import raw

ChannelAdminLogEventsFilter = Union[raw.types.ChannelAdminLogEventsFilter]


# noinspection PyRedeclaration
class ChannelAdminLogEventsFilter:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChannelAdminLogEventsFilter <pyeitaa.raw.types.ChannelAdminLogEventsFilter>`
    """

    QUALNAME = "pyeitaa.raw.base.ChannelAdminLogEventsFilter"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
