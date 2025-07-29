from typing import Union
from pyeitaa import raw

InputBotInlineMessageID = Union[raw.types.InputBotInlineMessageID, raw.types.InputBotInlineMessageID64]


# noinspection PyRedeclaration
class InputBotInlineMessageID:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputBotInlineMessageID <pyeitaa.raw.types.InputBotInlineMessageID>`
            - :obj:`InputBotInlineMessageID64 <pyeitaa.raw.types.InputBotInlineMessageID64>`
    """

    QUALNAME = "pyeitaa.raw.base.InputBotInlineMessageID"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
