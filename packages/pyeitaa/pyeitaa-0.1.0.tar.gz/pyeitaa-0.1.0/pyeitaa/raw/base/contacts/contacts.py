from typing import Union
from pyeitaa import raw

Contacts = Union[raw.types.contacts.Contacts, raw.types.contacts.ContactsNotModified]


# noinspection PyRedeclaration
class Contacts:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`contacts.Contacts <pyeitaa.raw.types.contacts.Contacts>`
            - :obj:`contacts.ContactsNotModified <pyeitaa.raw.types.contacts.ContactsNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.GetContacts <pyeitaa.raw.functions.contacts.GetContacts>`
    """

    QUALNAME = "pyeitaa.raw.base.contacts.Contacts"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
