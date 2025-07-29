from typing import Union
from pyeitaa import raw

BotCallbackAnswer = Union[raw.types.messages.BotCallbackAnswer]


# noinspection PyRedeclaration
class BotCallbackAnswer:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.BotCallbackAnswer <pyeitaa.raw.types.messages.BotCallbackAnswer>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetBotCallbackAnswer <pyeitaa.raw.functions.messages.GetBotCallbackAnswer>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.BotCallbackAnswer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
