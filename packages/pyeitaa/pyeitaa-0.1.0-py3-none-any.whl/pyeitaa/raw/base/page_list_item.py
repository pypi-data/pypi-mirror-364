from typing import Union
from pyeitaa import raw

PageListItem = Union[raw.types.PageListItemBlocks, raw.types.PageListItemText]


# noinspection PyRedeclaration
class PageListItem:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PageListItemBlocks <pyeitaa.raw.types.PageListItemBlocks>`
            - :obj:`PageListItemText <pyeitaa.raw.types.PageListItemText>`
    """

    QUALNAME = "pyeitaa.raw.base.PageListItem"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
