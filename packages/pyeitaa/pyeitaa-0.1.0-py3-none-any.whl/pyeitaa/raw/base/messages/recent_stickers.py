from typing import Union
from pyeitaa import raw

RecentStickers = Union[raw.types.messages.RecentStickers, raw.types.messages.RecentStickersNotModified]


# noinspection PyRedeclaration
class RecentStickers:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.RecentStickers <pyeitaa.raw.types.messages.RecentStickers>`
            - :obj:`messages.RecentStickersNotModified <pyeitaa.raw.types.messages.RecentStickersNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetRecentStickers <pyeitaa.raw.functions.messages.GetRecentStickers>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.RecentStickers"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
