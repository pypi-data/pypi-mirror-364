from typing import Union
from pyeitaa import raw

InputStickerSet = Union[raw.types.InputStickerSetAnimatedEmoji, raw.types.InputStickerSetDice, raw.types.InputStickerSetEmpty, raw.types.InputStickerSetID, raw.types.InputStickerSetShortName]


# noinspection PyRedeclaration
class InputStickerSet:
    """This base type has 5 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputStickerSetAnimatedEmoji <pyeitaa.raw.types.InputStickerSetAnimatedEmoji>`
            - :obj:`InputStickerSetDice <pyeitaa.raw.types.InputStickerSetDice>`
            - :obj:`InputStickerSetEmpty <pyeitaa.raw.types.InputStickerSetEmpty>`
            - :obj:`InputStickerSetID <pyeitaa.raw.types.InputStickerSetID>`
            - :obj:`InputStickerSetShortName <pyeitaa.raw.types.InputStickerSetShortName>`
    """

    QUALNAME = "pyeitaa.raw.base.InputStickerSet"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
