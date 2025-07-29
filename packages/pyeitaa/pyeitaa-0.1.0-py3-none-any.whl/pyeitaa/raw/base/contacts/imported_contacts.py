from typing import Union
from pyeitaa import raw

ImportedContacts = Union[raw.types.contacts.ImportedContacts]


# noinspection PyRedeclaration
class ImportedContacts:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`contacts.ImportedContacts <pyeitaa.raw.types.contacts.ImportedContacts>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.ImportContacts <pyeitaa.raw.functions.contacts.ImportContacts>`
    """

    QUALNAME = "pyeitaa.raw.base.contacts.ImportedContacts"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
