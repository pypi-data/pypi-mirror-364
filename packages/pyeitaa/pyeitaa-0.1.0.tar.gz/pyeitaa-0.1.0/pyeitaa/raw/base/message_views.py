from typing import Union
from pyeitaa import raw

MessageViews = Union[raw.types.MessageViews]


# noinspection PyRedeclaration
class MessageViews:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MessageViews <pyeitaa.raw.types.MessageViews>`
    """

    QUALNAME = "pyeitaa.raw.base.MessageViews"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
