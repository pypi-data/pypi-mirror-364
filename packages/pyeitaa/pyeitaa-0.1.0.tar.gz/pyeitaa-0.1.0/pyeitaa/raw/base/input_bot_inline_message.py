from typing import Union
from pyeitaa import raw

InputBotInlineMessage = Union[raw.types.InputBotInlineMessageGame, raw.types.InputBotInlineMessageMediaAuto, raw.types.InputBotInlineMessageMediaContact, raw.types.InputBotInlineMessageMediaGeo, raw.types.InputBotInlineMessageMediaInvoice, raw.types.InputBotInlineMessageMediaVenue, raw.types.InputBotInlineMessageText]


# noinspection PyRedeclaration
class InputBotInlineMessage:
    """This base type has 7 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputBotInlineMessageGame <pyeitaa.raw.types.InputBotInlineMessageGame>`
            - :obj:`InputBotInlineMessageMediaAuto <pyeitaa.raw.types.InputBotInlineMessageMediaAuto>`
            - :obj:`InputBotInlineMessageMediaContact <pyeitaa.raw.types.InputBotInlineMessageMediaContact>`
            - :obj:`InputBotInlineMessageMediaGeo <pyeitaa.raw.types.InputBotInlineMessageMediaGeo>`
            - :obj:`InputBotInlineMessageMediaInvoice <pyeitaa.raw.types.InputBotInlineMessageMediaInvoice>`
            - :obj:`InputBotInlineMessageMediaVenue <pyeitaa.raw.types.InputBotInlineMessageMediaVenue>`
            - :obj:`InputBotInlineMessageText <pyeitaa.raw.types.InputBotInlineMessageText>`
    """

    QUALNAME = "pyeitaa.raw.base.InputBotInlineMessage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
