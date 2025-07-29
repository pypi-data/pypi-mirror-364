from typing import Union
from pyeitaa import raw

Chat = Union[raw.types.Channel, raw.types.ChannelForbidden, raw.types.Chat, raw.types.ChatEmpty, raw.types.ChatForbidden]


# noinspection PyRedeclaration
class Chat:
    """This base type has 5 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Channel <pyeitaa.raw.types.Channel>`
            - :obj:`ChannelForbidden <pyeitaa.raw.types.ChannelForbidden>`
            - :obj:`Chat <pyeitaa.raw.types.Chat>`
            - :obj:`ChatEmpty <pyeitaa.raw.types.ChatEmpty>`
            - :obj:`ChatForbidden <pyeitaa.raw.types.ChatForbidden>`
    """

    QUALNAME = "pyeitaa.raw.base.Chat"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
