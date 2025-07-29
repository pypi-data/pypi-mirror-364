from typing import Union
from pyeitaa import raw

DialogPeer = Union[raw.types.DialogPeer, raw.types.DialogPeerFolder]


# noinspection PyRedeclaration
class DialogPeer:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`DialogPeer <pyeitaa.raw.types.DialogPeer>`
            - :obj:`DialogPeerFolder <pyeitaa.raw.types.DialogPeerFolder>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetDialogUnreadMarks <pyeitaa.raw.functions.messages.GetDialogUnreadMarks>`
    """

    QUALNAME = "pyeitaa.raw.base.DialogPeer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
