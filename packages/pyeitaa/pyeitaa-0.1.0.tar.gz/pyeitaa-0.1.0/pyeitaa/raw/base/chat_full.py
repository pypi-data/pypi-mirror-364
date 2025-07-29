from typing import Union
from pyeitaa import raw

ChatFull = Union[raw.types.ChannelFull, raw.types.ChatFull]


# noinspection PyRedeclaration
class ChatFull:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChannelFull <pyeitaa.raw.types.ChannelFull>`
            - :obj:`ChatFull <pyeitaa.raw.types.ChatFull>`
    """

    QUALNAME = "pyeitaa.raw.base.ChatFull"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
