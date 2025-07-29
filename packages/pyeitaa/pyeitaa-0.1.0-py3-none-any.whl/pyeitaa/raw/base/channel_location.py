from typing import Union
from pyeitaa import raw

ChannelLocation = Union[raw.types.ChannelLocation, raw.types.ChannelLocationEmpty]


# noinspection PyRedeclaration
class ChannelLocation:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChannelLocation <pyeitaa.raw.types.ChannelLocation>`
            - :obj:`ChannelLocationEmpty <pyeitaa.raw.types.ChannelLocationEmpty>`
    """

    QUALNAME = "pyeitaa.raw.base.ChannelLocation"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
