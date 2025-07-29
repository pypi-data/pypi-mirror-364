from typing import Union
from pyeitaa import raw

PageTableRow = Union[raw.types.PageTableRow]


# noinspection PyRedeclaration
class PageTableRow:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PageTableRow <pyeitaa.raw.types.PageTableRow>`
    """

    QUALNAME = "pyeitaa.raw.base.PageTableRow"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
