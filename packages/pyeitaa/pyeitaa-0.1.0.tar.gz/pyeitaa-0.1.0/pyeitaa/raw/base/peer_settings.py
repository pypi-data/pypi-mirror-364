from typing import Union
from pyeitaa import raw

PeerSettings = Union[raw.types.PeerSettings]


# noinspection PyRedeclaration
class PeerSettings:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PeerSettings <pyeitaa.raw.types.PeerSettings>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetPeerSettings <pyeitaa.raw.functions.messages.GetPeerSettings>`
    """

    QUALNAME = "pyeitaa.raw.base.PeerSettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
