from typing import Union
from pyeitaa import raw

PopularContact = Union[raw.types.PopularContact]


# noinspection PyRedeclaration
class PopularContact:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PopularContact <pyeitaa.raw.types.PopularContact>`
    """

    QUALNAME = "pyeitaa.raw.base.PopularContact"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
