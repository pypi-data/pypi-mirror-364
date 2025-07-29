from typing import Union
from pyeitaa import raw

PeerLocated = Union[raw.types.PeerLocated, raw.types.PeerSelfLocated]


# noinspection PyRedeclaration
class PeerLocated:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PeerLocated <pyeitaa.raw.types.PeerLocated>`
            - :obj:`PeerSelfLocated <pyeitaa.raw.types.PeerSelfLocated>`
    """

    QUALNAME = "pyeitaa.raw.base.PeerLocated"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
