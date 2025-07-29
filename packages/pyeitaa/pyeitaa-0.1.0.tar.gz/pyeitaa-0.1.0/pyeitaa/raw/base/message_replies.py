from typing import Union
from pyeitaa import raw

MessageReplies = Union[raw.types.MessageReplies]


# noinspection PyRedeclaration
class MessageReplies:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MessageReplies <pyeitaa.raw.types.MessageReplies>`
    """

    QUALNAME = "pyeitaa.raw.base.MessageReplies"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
