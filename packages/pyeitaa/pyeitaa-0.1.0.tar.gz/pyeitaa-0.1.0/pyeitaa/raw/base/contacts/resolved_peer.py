from typing import Union
from pyeitaa import raw

ResolvedPeer = Union[raw.types.contacts.ResolvedPeer]


# noinspection PyRedeclaration
class ResolvedPeer:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`contacts.ResolvedPeer <pyeitaa.raw.types.contacts.ResolvedPeer>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.ResolveUsername <pyeitaa.raw.functions.contacts.ResolveUsername>`
    """

    QUALNAME = "pyeitaa.raw.base.contacts.ResolvedPeer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
