from typing import Union
from pyeitaa import raw

NotifyPeer = Union[raw.types.NotifyBroadcasts, raw.types.NotifyChats, raw.types.NotifyPeer, raw.types.NotifyUsers]


# noinspection PyRedeclaration
class NotifyPeer:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`NotifyBroadcasts <pyeitaa.raw.types.NotifyBroadcasts>`
            - :obj:`NotifyChats <pyeitaa.raw.types.NotifyChats>`
            - :obj:`NotifyPeer <pyeitaa.raw.types.NotifyPeer>`
            - :obj:`NotifyUsers <pyeitaa.raw.types.NotifyUsers>`
    """

    QUALNAME = "pyeitaa.raw.base.NotifyPeer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
