from typing import Union
from pyeitaa import raw

InlineQueryPeerType = Union[raw.types.InlineQueryPeerTypeBroadcast, raw.types.InlineQueryPeerTypeChat, raw.types.InlineQueryPeerTypeMegagroup, raw.types.InlineQueryPeerTypePM, raw.types.InlineQueryPeerTypeSameBotPM]


# noinspection PyRedeclaration
class InlineQueryPeerType:
    """This base type has 5 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InlineQueryPeerTypeBroadcast <pyeitaa.raw.types.InlineQueryPeerTypeBroadcast>`
            - :obj:`InlineQueryPeerTypeChat <pyeitaa.raw.types.InlineQueryPeerTypeChat>`
            - :obj:`InlineQueryPeerTypeMegagroup <pyeitaa.raw.types.InlineQueryPeerTypeMegagroup>`
            - :obj:`InlineQueryPeerTypePM <pyeitaa.raw.types.InlineQueryPeerTypePM>`
            - :obj:`InlineQueryPeerTypeSameBotPM <pyeitaa.raw.types.InlineQueryPeerTypeSameBotPM>`
    """

    QUALNAME = "pyeitaa.raw.base.InlineQueryPeerType"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
