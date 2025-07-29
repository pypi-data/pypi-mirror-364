from typing import Union
from pyeitaa import raw

MessageCopy = Union[raw.types.MsgCopy]


# noinspection PyRedeclaration
class MessageCopy:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MsgCopy <pyeitaa.raw.types.MsgCopy>`
    """

    QUALNAME = "pyeitaa.raw.base.MessageCopy"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
