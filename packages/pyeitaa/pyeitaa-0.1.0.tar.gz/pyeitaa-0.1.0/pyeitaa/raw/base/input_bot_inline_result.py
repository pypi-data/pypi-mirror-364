from typing import Union
from pyeitaa import raw

InputBotInlineResult = Union[raw.types.InputBotInlineResult, raw.types.InputBotInlineResultDocument, raw.types.InputBotInlineResultGame, raw.types.InputBotInlineResultPhoto]


# noinspection PyRedeclaration
class InputBotInlineResult:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputBotInlineResult <pyeitaa.raw.types.InputBotInlineResult>`
            - :obj:`InputBotInlineResultDocument <pyeitaa.raw.types.InputBotInlineResultDocument>`
            - :obj:`InputBotInlineResultGame <pyeitaa.raw.types.InputBotInlineResultGame>`
            - :obj:`InputBotInlineResultPhoto <pyeitaa.raw.types.InputBotInlineResultPhoto>`
    """

    QUALNAME = "pyeitaa.raw.base.InputBotInlineResult"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
