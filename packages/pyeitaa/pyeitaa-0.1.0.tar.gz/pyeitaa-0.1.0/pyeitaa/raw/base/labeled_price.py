from typing import Union
from pyeitaa import raw

LabeledPrice = Union[raw.types.LabeledPrice]


# noinspection PyRedeclaration
class LabeledPrice:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`LabeledPrice <pyeitaa.raw.types.LabeledPrice>`
    """

    QUALNAME = "pyeitaa.raw.base.LabeledPrice"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
