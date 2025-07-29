from typing import Union
from pyeitaa import raw

ContactStatus = Union[raw.types.ContactStatus]


# noinspection PyRedeclaration
class ContactStatus:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ContactStatus <pyeitaa.raw.types.ContactStatus>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.GetStatuses <pyeitaa.raw.functions.contacts.GetStatuses>`
    """

    QUALNAME = "pyeitaa.raw.base.ContactStatus"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
