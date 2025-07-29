from typing import Union
from pyeitaa import raw

EmojiKeywordsDifference = Union[raw.types.EmojiKeywordsDifference]


# noinspection PyRedeclaration
class EmojiKeywordsDifference:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EmojiKeywordsDifference <pyeitaa.raw.types.EmojiKeywordsDifference>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetEmojiKeywords <pyeitaa.raw.functions.messages.GetEmojiKeywords>`
            - :obj:`messages.GetEmojiKeywordsDifference <pyeitaa.raw.functions.messages.GetEmojiKeywordsDifference>`
    """

    QUALNAME = "pyeitaa.raw.base.EmojiKeywordsDifference"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
