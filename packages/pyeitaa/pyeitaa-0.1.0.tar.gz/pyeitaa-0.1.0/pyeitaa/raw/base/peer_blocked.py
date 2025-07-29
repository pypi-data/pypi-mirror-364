from typing import Union
from pyeitaa import raw

PeerBlocked = Union[raw.types.PeerBlocked]


# noinspection PyRedeclaration
class PeerBlocked:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PeerBlocked <pyeitaa.raw.types.PeerBlocked>`
    """

    QUALNAME = "pyeitaa.raw.base.PeerBlocked"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
