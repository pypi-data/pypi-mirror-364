from typing import Union
from pyeitaa import raw

InputDialogPeer = Union[raw.types.InputDialogPeer, raw.types.InputDialogPeerFolder]


# noinspection PyRedeclaration
class InputDialogPeer:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputDialogPeer <pyeitaa.raw.types.InputDialogPeer>`
            - :obj:`InputDialogPeerFolder <pyeitaa.raw.types.InputDialogPeerFolder>`
    """

    QUALNAME = "pyeitaa.raw.base.InputDialogPeer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
