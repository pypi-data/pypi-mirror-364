from typing import Union
from pyeitaa import raw

RecentMeUrl = Union[raw.types.RecentMeUrlChat, raw.types.RecentMeUrlChatInvite, raw.types.RecentMeUrlStickerSet, raw.types.RecentMeUrlUnknown, raw.types.RecentMeUrlUser]


# noinspection PyRedeclaration
class RecentMeUrl:
    """This base type has 5 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`RecentMeUrlChat <pyeitaa.raw.types.RecentMeUrlChat>`
            - :obj:`RecentMeUrlChatInvite <pyeitaa.raw.types.RecentMeUrlChatInvite>`
            - :obj:`RecentMeUrlStickerSet <pyeitaa.raw.types.RecentMeUrlStickerSet>`
            - :obj:`RecentMeUrlUnknown <pyeitaa.raw.types.RecentMeUrlUnknown>`
            - :obj:`RecentMeUrlUser <pyeitaa.raw.types.RecentMeUrlUser>`
    """

    QUALNAME = "pyeitaa.raw.base.RecentMeUrl"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
