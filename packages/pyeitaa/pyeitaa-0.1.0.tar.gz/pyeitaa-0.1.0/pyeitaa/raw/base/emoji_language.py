from typing import Union
from pyeitaa import raw

EmojiLanguage = Union[raw.types.EmojiLanguage]


# noinspection PyRedeclaration
class EmojiLanguage:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EmojiLanguage <pyeitaa.raw.types.EmojiLanguage>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetEmojiKeywordsLanguages <pyeitaa.raw.functions.messages.GetEmojiKeywordsLanguages>`
    """

    QUALNAME = "pyeitaa.raw.base.EmojiLanguage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
