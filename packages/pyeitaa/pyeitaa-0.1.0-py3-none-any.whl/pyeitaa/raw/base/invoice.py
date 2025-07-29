from typing import Union
from pyeitaa import raw

Invoice = Union[raw.types.Invoice]


# noinspection PyRedeclaration
class Invoice:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Invoice <pyeitaa.raw.types.Invoice>`
    """

    QUALNAME = "pyeitaa.raw.base.Invoice"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
