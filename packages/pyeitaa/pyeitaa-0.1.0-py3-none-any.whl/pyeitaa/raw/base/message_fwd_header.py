from typing import Union
from pyeitaa import raw

MessageFwdHeader = Union[raw.types.MessageFwdHeader]


# noinspection PyRedeclaration
class MessageFwdHeader:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MessageFwdHeader <pyeitaa.raw.types.MessageFwdHeader>`
    """

    QUALNAME = "pyeitaa.raw.base.MessageFwdHeader"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
