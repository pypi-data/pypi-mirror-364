from typing import Union
from pyeitaa import raw

InputFolderPeer = Union[raw.types.InputFolderPeer]


# noinspection PyRedeclaration
class InputFolderPeer:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputFolderPeer <pyeitaa.raw.types.InputFolderPeer>`
    """

    QUALNAME = "pyeitaa.raw.base.InputFolderPeer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
