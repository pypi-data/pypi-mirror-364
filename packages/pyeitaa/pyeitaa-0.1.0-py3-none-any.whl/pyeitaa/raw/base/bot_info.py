from typing import Union
from pyeitaa import raw

BotInfo = Union[raw.types.BotInfo]


# noinspection PyRedeclaration
class BotInfo:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`BotInfo <pyeitaa.raw.types.BotInfo>`
    """

    QUALNAME = "pyeitaa.raw.base.BotInfo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
