from typing import Union
from pyeitaa import raw

Peer = Union[raw.types.PeerChannel, raw.types.PeerChat, raw.types.PeerUser]


# noinspection PyRedeclaration
class Peer:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PeerChannel <pyeitaa.raw.types.PeerChannel>`
            - :obj:`PeerChat <pyeitaa.raw.types.PeerChat>`
            - :obj:`PeerUser <pyeitaa.raw.types.PeerUser>`
    """

    QUALNAME = "pyeitaa.raw.base.Peer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
