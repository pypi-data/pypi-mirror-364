from typing import Union
from pyeitaa import raw

FoundStickerSets = Union[raw.types.messages.FoundStickerSets, raw.types.messages.FoundStickerSetsNotModified]


# noinspection PyRedeclaration
class FoundStickerSets:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.FoundStickerSets <pyeitaa.raw.types.messages.FoundStickerSets>`
            - :obj:`messages.FoundStickerSetsNotModified <pyeitaa.raw.types.messages.FoundStickerSetsNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.SearchStickerSets <pyeitaa.raw.functions.messages.SearchStickerSets>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.FoundStickerSets"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
