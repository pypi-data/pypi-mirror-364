from typing import Union
from pyeitaa import raw

StickerSetCovered = Union[raw.types.StickerSetCovered, raw.types.StickerSetMultiCovered]


# noinspection PyRedeclaration
class StickerSetCovered:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`StickerSetCovered <pyeitaa.raw.types.StickerSetCovered>`
            - :obj:`StickerSetMultiCovered <pyeitaa.raw.types.StickerSetMultiCovered>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetAttachedStickers <pyeitaa.raw.functions.messages.GetAttachedStickers>`
    """

    QUALNAME = "pyeitaa.raw.base.StickerSetCovered"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
