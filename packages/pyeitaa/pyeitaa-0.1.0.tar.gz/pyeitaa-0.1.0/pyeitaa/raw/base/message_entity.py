from typing import Union
from pyeitaa import raw

MessageEntity = Union[raw.types.InputMessageEntityMentionName, raw.types.MessageEntityBankCard, raw.types.MessageEntityBlockquote, raw.types.MessageEntityBold, raw.types.MessageEntityBotCommand, raw.types.MessageEntityCashtag, raw.types.MessageEntityCode, raw.types.MessageEntityEmail, raw.types.MessageEntityHashtag, raw.types.MessageEntityItalic, raw.types.MessageEntityMention, raw.types.MessageEntityMentionName, raw.types.MessageEntityPhone, raw.types.MessageEntityPre, raw.types.MessageEntityStrike, raw.types.MessageEntityTextUrl, raw.types.MessageEntityUnderline, raw.types.MessageEntityUnknown, raw.types.MessageEntityUrl]


# noinspection PyRedeclaration
class MessageEntity:
    """This base type has 19 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputMessageEntityMentionName <pyeitaa.raw.types.InputMessageEntityMentionName>`
            - :obj:`MessageEntityBankCard <pyeitaa.raw.types.MessageEntityBankCard>`
            - :obj:`MessageEntityBlockquote <pyeitaa.raw.types.MessageEntityBlockquote>`
            - :obj:`MessageEntityBold <pyeitaa.raw.types.MessageEntityBold>`
            - :obj:`MessageEntityBotCommand <pyeitaa.raw.types.MessageEntityBotCommand>`
            - :obj:`MessageEntityCashtag <pyeitaa.raw.types.MessageEntityCashtag>`
            - :obj:`MessageEntityCode <pyeitaa.raw.types.MessageEntityCode>`
            - :obj:`MessageEntityEmail <pyeitaa.raw.types.MessageEntityEmail>`
            - :obj:`MessageEntityHashtag <pyeitaa.raw.types.MessageEntityHashtag>`
            - :obj:`MessageEntityItalic <pyeitaa.raw.types.MessageEntityItalic>`
            - :obj:`MessageEntityMention <pyeitaa.raw.types.MessageEntityMention>`
            - :obj:`MessageEntityMentionName <pyeitaa.raw.types.MessageEntityMentionName>`
            - :obj:`MessageEntityPhone <pyeitaa.raw.types.MessageEntityPhone>`
            - :obj:`MessageEntityPre <pyeitaa.raw.types.MessageEntityPre>`
            - :obj:`MessageEntityStrike <pyeitaa.raw.types.MessageEntityStrike>`
            - :obj:`MessageEntityTextUrl <pyeitaa.raw.types.MessageEntityTextUrl>`
            - :obj:`MessageEntityUnderline <pyeitaa.raw.types.MessageEntityUnderline>`
            - :obj:`MessageEntityUnknown <pyeitaa.raw.types.MessageEntityUnknown>`
            - :obj:`MessageEntityUrl <pyeitaa.raw.types.MessageEntityUrl>`
    """

    QUALNAME = "pyeitaa.raw.base.MessageEntity"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
