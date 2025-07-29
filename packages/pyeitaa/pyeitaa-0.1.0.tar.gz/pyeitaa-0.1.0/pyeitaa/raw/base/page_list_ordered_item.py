from typing import Union
from pyeitaa import raw

PageListOrderedItem = Union[raw.types.PageListOrderedItemBlocks, raw.types.PageListOrderedItemText]


# noinspection PyRedeclaration
class PageListOrderedItem:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PageListOrderedItemBlocks <pyeitaa.raw.types.PageListOrderedItemBlocks>`
            - :obj:`PageListOrderedItemText <pyeitaa.raw.types.PageListOrderedItemText>`
    """

    QUALNAME = "pyeitaa.raw.base.PageListOrderedItem"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
