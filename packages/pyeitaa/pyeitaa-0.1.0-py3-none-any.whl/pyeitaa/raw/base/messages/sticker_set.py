from typing import Union
from pyeitaa import raw

StickerSet = Union[raw.types.messages.StickerSet]


# noinspection PyRedeclaration
class StickerSet:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.StickerSet <pyeitaa.raw.types.messages.StickerSet>`

    See Also:
        This object can be returned by 6 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetStickerSet <pyeitaa.raw.functions.messages.GetStickerSet>`
            - :obj:`stickers.CreateStickerSet <pyeitaa.raw.functions.stickers.CreateStickerSet>`
            - :obj:`stickers.RemoveStickerFromSet <pyeitaa.raw.functions.stickers.RemoveStickerFromSet>`
            - :obj:`stickers.ChangeStickerPosition <pyeitaa.raw.functions.stickers.ChangeStickerPosition>`
            - :obj:`stickers.AddStickerToSet <pyeitaa.raw.functions.stickers.AddStickerToSet>`
            - :obj:`stickers.SetStickerSetThumb <pyeitaa.raw.functions.stickers.SetStickerSetThumb>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.StickerSet"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
