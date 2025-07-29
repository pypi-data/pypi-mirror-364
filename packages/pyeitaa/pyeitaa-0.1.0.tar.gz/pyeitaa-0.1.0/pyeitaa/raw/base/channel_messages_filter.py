from typing import Union
from pyeitaa import raw

ChannelMessagesFilter = Union[raw.types.ChannelMessagesFilter, raw.types.ChannelMessagesFilterEmpty]


# noinspection PyRedeclaration
class ChannelMessagesFilter:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChannelMessagesFilter <pyeitaa.raw.types.ChannelMessagesFilter>`
            - :obj:`ChannelMessagesFilterEmpty <pyeitaa.raw.types.ChannelMessagesFilterEmpty>`
    """

    QUALNAME = "pyeitaa.raw.base.ChannelMessagesFilter"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
