from typing import Union
from pyeitaa import raw

Contact = Union[raw.types.Contact]


# noinspection PyRedeclaration
class Contact:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Contact <pyeitaa.raw.types.Contact>`
    """

    QUALNAME = "pyeitaa.raw.base.Contact"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
