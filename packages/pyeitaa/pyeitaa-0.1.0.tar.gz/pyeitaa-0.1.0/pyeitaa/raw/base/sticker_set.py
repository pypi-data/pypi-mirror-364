from typing import Union
from pyeitaa import raw

StickerSet = Union[raw.types.StickerSet]


# noinspection PyRedeclaration
class StickerSet:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`StickerSet <pyeitaa.raw.types.StickerSet>`
    """

    QUALNAME = "pyeitaa.raw.base.StickerSet"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
