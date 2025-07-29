from typing import Union
from pyeitaa import raw

Stickers = Union[raw.types.messages.Stickers, raw.types.messages.StickersNotModified]


# noinspection PyRedeclaration
class Stickers:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.Stickers <pyeitaa.raw.types.messages.Stickers>`
            - :obj:`messages.StickersNotModified <pyeitaa.raw.types.messages.StickersNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetStickers <pyeitaa.raw.functions.messages.GetStickers>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.Stickers"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
