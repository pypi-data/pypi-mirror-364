from typing import Union
from pyeitaa import raw

BotCommand = Union[raw.types.BotCommand]


# noinspection PyRedeclaration
class BotCommand:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`BotCommand <pyeitaa.raw.types.BotCommand>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`bots.GetBotCommands <pyeitaa.raw.functions.bots.GetBotCommands>`
    """

    QUALNAME = "pyeitaa.raw.base.BotCommand"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
