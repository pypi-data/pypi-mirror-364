from typing import Union
from pyeitaa import raw

BotInlineMessage = Union[raw.types.BotInlineMessageMediaAuto, raw.types.BotInlineMessageMediaContact, raw.types.BotInlineMessageMediaGeo, raw.types.BotInlineMessageMediaInvoice, raw.types.BotInlineMessageMediaVenue, raw.types.BotInlineMessageText]


# noinspection PyRedeclaration
class BotInlineMessage:
    """This base type has 6 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`BotInlineMessageMediaAuto <pyeitaa.raw.types.BotInlineMessageMediaAuto>`
            - :obj:`BotInlineMessageMediaContact <pyeitaa.raw.types.BotInlineMessageMediaContact>`
            - :obj:`BotInlineMessageMediaGeo <pyeitaa.raw.types.BotInlineMessageMediaGeo>`
            - :obj:`BotInlineMessageMediaInvoice <pyeitaa.raw.types.BotInlineMessageMediaInvoice>`
            - :obj:`BotInlineMessageMediaVenue <pyeitaa.raw.types.BotInlineMessageMediaVenue>`
            - :obj:`BotInlineMessageText <pyeitaa.raw.types.BotInlineMessageText>`
    """

    QUALNAME = "pyeitaa.raw.base.BotInlineMessage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
