from typing import Union
from pyeitaa import raw

InputNotifyPeer = Union[raw.types.InputNotifyBroadcasts, raw.types.InputNotifyChats, raw.types.InputNotifyPeer, raw.types.InputNotifyUsers]


# noinspection PyRedeclaration
class InputNotifyPeer:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputNotifyBroadcasts <pyeitaa.raw.types.InputNotifyBroadcasts>`
            - :obj:`InputNotifyChats <pyeitaa.raw.types.InputNotifyChats>`
            - :obj:`InputNotifyPeer <pyeitaa.raw.types.InputNotifyPeer>`
            - :obj:`InputNotifyUsers <pyeitaa.raw.types.InputNotifyUsers>`
    """

    QUALNAME = "pyeitaa.raw.base.InputNotifyPeer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
