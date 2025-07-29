from typing import Union
from pyeitaa import raw

PeerDialogs = Union[raw.types.messages.PeerDialogs]


# noinspection PyRedeclaration
class PeerDialogs:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.PeerDialogs <pyeitaa.raw.types.messages.PeerDialogs>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetPeerDialogs <pyeitaa.raw.functions.messages.GetPeerDialogs>`
            - :obj:`messages.GetPinnedDialogs <pyeitaa.raw.functions.messages.GetPinnedDialogs>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.PeerDialogs"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
