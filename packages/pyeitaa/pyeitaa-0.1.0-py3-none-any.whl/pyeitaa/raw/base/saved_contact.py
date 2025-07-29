from typing import Union
from pyeitaa import raw

SavedContact = Union[raw.types.SavedPhoneContact]


# noinspection PyRedeclaration
class SavedContact:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SavedPhoneContact <pyeitaa.raw.types.SavedPhoneContact>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.GetSaved <pyeitaa.raw.functions.contacts.GetSaved>`
    """

    QUALNAME = "pyeitaa.raw.base.SavedContact"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
