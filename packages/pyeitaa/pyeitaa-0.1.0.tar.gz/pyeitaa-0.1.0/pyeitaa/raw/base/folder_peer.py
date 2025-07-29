from typing import Union
from pyeitaa import raw

FolderPeer = Union[raw.types.FolderPeer]


# noinspection PyRedeclaration
class FolderPeer:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`FolderPeer <pyeitaa.raw.types.FolderPeer>`
    """

    QUALNAME = "pyeitaa.raw.base.FolderPeer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
