from typing import Union
from pyeitaa import raw

BotCommandScope = Union[raw.types.BotCommandScopeChatAdmins, raw.types.BotCommandScopeChats, raw.types.BotCommandScopeDefault, raw.types.BotCommandScopePeer, raw.types.BotCommandScopePeerAdmins, raw.types.BotCommandScopePeerUser, raw.types.BotCommandScopeUsers]


# noinspection PyRedeclaration
class BotCommandScope:
    """This base type has 7 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`BotCommandScopeChatAdmins <pyeitaa.raw.types.BotCommandScopeChatAdmins>`
            - :obj:`BotCommandScopeChats <pyeitaa.raw.types.BotCommandScopeChats>`
            - :obj:`BotCommandScopeDefault <pyeitaa.raw.types.BotCommandScopeDefault>`
            - :obj:`BotCommandScopePeer <pyeitaa.raw.types.BotCommandScopePeer>`
            - :obj:`BotCommandScopePeerAdmins <pyeitaa.raw.types.BotCommandScopePeerAdmins>`
            - :obj:`BotCommandScopePeerUser <pyeitaa.raw.types.BotCommandScopePeerUser>`
            - :obj:`BotCommandScopeUsers <pyeitaa.raw.types.BotCommandScopeUsers>`
    """

    QUALNAME = "pyeitaa.raw.base.BotCommandScope"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
