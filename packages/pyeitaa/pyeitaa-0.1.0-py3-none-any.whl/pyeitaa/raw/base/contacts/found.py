from typing import Union
from pyeitaa import raw

Found = Union[raw.types.contacts.Found]


# noinspection PyRedeclaration
class Found:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`contacts.Found <pyeitaa.raw.types.contacts.Found>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.Search <pyeitaa.raw.functions.contacts.Search>`
    """

    QUALNAME = "pyeitaa.raw.base.contacts.Found"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
