from typing import Union
from pyeitaa import raw

ChatFull = Union[raw.types.messages.ChatFull]


# noinspection PyRedeclaration
class ChatFull:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.ChatFull <pyeitaa.raw.types.messages.ChatFull>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetFullChat <pyeitaa.raw.functions.messages.GetFullChat>`
            - :obj:`channels.GetFullChannel <pyeitaa.raw.functions.channels.GetFullChannel>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.ChatFull"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
