from typing import Union
from pyeitaa import raw

PageCaption = Union[raw.types.PageCaption]


# noinspection PyRedeclaration
class PageCaption:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PageCaption <pyeitaa.raw.types.PageCaption>`
    """

    QUALNAME = "pyeitaa.raw.base.PageCaption"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
