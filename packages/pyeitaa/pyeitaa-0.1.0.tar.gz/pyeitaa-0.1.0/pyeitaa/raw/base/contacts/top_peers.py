from typing import Union
from pyeitaa import raw

TopPeers = Union[raw.types.contacts.TopPeers, raw.types.contacts.TopPeersDisabled, raw.types.contacts.TopPeersNotModified]


# noinspection PyRedeclaration
class TopPeers:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`contacts.TopPeers <pyeitaa.raw.types.contacts.TopPeers>`
            - :obj:`contacts.TopPeersDisabled <pyeitaa.raw.types.contacts.TopPeersDisabled>`
            - :obj:`contacts.TopPeersNotModified <pyeitaa.raw.types.contacts.TopPeersNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.GetTopPeers <pyeitaa.raw.functions.contacts.GetTopPeers>`
    """

    QUALNAME = "pyeitaa.raw.base.contacts.TopPeers"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
