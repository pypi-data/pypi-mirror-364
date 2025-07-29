from typing import Union
from pyeitaa import raw

BotInlineResult = Union[raw.types.BotInlineMediaResult, raw.types.BotInlineResult]


# noinspection PyRedeclaration
class BotInlineResult:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`BotInlineMediaResult <pyeitaa.raw.types.BotInlineMediaResult>`
            - :obj:`BotInlineResult <pyeitaa.raw.types.BotInlineResult>`
    """

    QUALNAME = "pyeitaa.raw.base.BotInlineResult"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
