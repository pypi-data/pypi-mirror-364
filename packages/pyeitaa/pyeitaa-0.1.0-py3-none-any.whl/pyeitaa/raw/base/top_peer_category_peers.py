from typing import Union
from pyeitaa import raw

TopPeerCategoryPeers = Union[raw.types.TopPeerCategoryPeers]


# noinspection PyRedeclaration
class TopPeerCategoryPeers:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`TopPeerCategoryPeers <pyeitaa.raw.types.TopPeerCategoryPeers>`
    """

    QUALNAME = "pyeitaa.raw.base.TopPeerCategoryPeers"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
