from typing import Union
from pyeitaa import raw

BotResults = Union[raw.types.messages.BotResults]


# noinspection PyRedeclaration
class BotResults:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.BotResults <pyeitaa.raw.types.messages.BotResults>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetInlineBotResults <pyeitaa.raw.functions.messages.GetInlineBotResults>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.BotResults"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
