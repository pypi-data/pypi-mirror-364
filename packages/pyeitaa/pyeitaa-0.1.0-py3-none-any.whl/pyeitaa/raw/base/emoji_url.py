from typing import Union
from pyeitaa import raw

EmojiURL = Union[raw.types.EmojiURL]


# noinspection PyRedeclaration
class EmojiURL:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EmojiURL <pyeitaa.raw.types.EmojiURL>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetEmojiURL <pyeitaa.raw.functions.messages.GetEmojiURL>`
    """

    QUALNAME = "pyeitaa.raw.base.EmojiURL"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
