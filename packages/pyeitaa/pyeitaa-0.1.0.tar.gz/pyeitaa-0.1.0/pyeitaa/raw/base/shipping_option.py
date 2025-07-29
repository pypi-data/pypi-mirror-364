from typing import Union
from pyeitaa import raw

ShippingOption = Union[raw.types.ShippingOption]


# noinspection PyRedeclaration
class ShippingOption:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ShippingOption <pyeitaa.raw.types.ShippingOption>`
    """

    QUALNAME = "pyeitaa.raw.base.ShippingOption"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
