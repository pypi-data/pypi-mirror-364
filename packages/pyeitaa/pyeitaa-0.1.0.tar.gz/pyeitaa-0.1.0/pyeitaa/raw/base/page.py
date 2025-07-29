from typing import Union
from pyeitaa import raw

Page = Union[raw.types.Page]


# noinspection PyRedeclaration
class Page:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Page <pyeitaa.raw.types.Page>`
    """

    QUALNAME = "pyeitaa.raw.base.Page"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
