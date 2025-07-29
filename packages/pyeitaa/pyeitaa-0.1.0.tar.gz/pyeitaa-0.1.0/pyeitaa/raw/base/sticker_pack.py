from typing import Union
from pyeitaa import raw

StickerPack = Union[raw.types.StickerPack]


# noinspection PyRedeclaration
class StickerPack:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`StickerPack <pyeitaa.raw.types.StickerPack>`
    """

    QUALNAME = "pyeitaa.raw.base.StickerPack"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
