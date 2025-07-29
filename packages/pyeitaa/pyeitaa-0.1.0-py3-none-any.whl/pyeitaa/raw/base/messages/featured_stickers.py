from typing import Union
from pyeitaa import raw

FeaturedStickers = Union[raw.types.messages.FeaturedStickers, raw.types.messages.FeaturedStickersNotModified]


# noinspection PyRedeclaration
class FeaturedStickers:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.FeaturedStickers <pyeitaa.raw.types.messages.FeaturedStickers>`
            - :obj:`messages.FeaturedStickersNotModified <pyeitaa.raw.types.messages.FeaturedStickersNotModified>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetFeaturedStickers <pyeitaa.raw.functions.messages.GetFeaturedStickers>`
            - :obj:`messages.GetOldFeaturedStickers <pyeitaa.raw.functions.messages.GetOldFeaturedStickers>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.FeaturedStickers"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
