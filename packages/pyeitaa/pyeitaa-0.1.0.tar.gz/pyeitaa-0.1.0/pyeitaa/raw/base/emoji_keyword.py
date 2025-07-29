from typing import Union
from pyeitaa import raw

EmojiKeyword = Union[raw.types.EmojiKeyword, raw.types.EmojiKeywordDeleted]


# noinspection PyRedeclaration
class EmojiKeyword:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EmojiKeyword <pyeitaa.raw.types.EmojiKeyword>`
            - :obj:`EmojiKeywordDeleted <pyeitaa.raw.types.EmojiKeywordDeleted>`
    """

    QUALNAME = "pyeitaa.raw.base.EmojiKeyword"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
