from typing import Union
from pyeitaa import raw

ReplyMarkup = Union[raw.types.ReplyInlineMarkup, raw.types.ReplyKeyboardForceReply, raw.types.ReplyKeyboardHide, raw.types.ReplyKeyboardMarkup]


# noinspection PyRedeclaration
class ReplyMarkup:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ReplyInlineMarkup <pyeitaa.raw.types.ReplyInlineMarkup>`
            - :obj:`ReplyKeyboardForceReply <pyeitaa.raw.types.ReplyKeyboardForceReply>`
            - :obj:`ReplyKeyboardHide <pyeitaa.raw.types.ReplyKeyboardHide>`
            - :obj:`ReplyKeyboardMarkup <pyeitaa.raw.types.ReplyKeyboardMarkup>`
    """

    QUALNAME = "pyeitaa.raw.base.ReplyMarkup"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
