from typing import Union
from pyeitaa import raw

ChatTheme = Union[raw.types.ChatTheme]


# noinspection PyRedeclaration
class ChatTheme:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChatTheme <pyeitaa.raw.types.ChatTheme>`
    """

    QUALNAME = "pyeitaa.raw.base.ChatTheme"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
