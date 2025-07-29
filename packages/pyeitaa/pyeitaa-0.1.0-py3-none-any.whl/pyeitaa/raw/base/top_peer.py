from typing import Union
from pyeitaa import raw

TopPeer = Union[raw.types.TopPeer]


# noinspection PyRedeclaration
class TopPeer:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`TopPeer <pyeitaa.raw.types.TopPeer>`
    """

    QUALNAME = "pyeitaa.raw.base.TopPeer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
