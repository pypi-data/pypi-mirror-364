from typing import Union
from pyeitaa import raw

Blocked = Union[raw.types.contacts.Blocked, raw.types.contacts.BlockedSlice]


# noinspection PyRedeclaration
class Blocked:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`contacts.Blocked <pyeitaa.raw.types.contacts.Blocked>`
            - :obj:`contacts.BlockedSlice <pyeitaa.raw.types.contacts.BlockedSlice>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.GetBlocked <pyeitaa.raw.functions.contacts.GetBlocked>`
    """

    QUALNAME = "pyeitaa.raw.base.contacts.Blocked"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
