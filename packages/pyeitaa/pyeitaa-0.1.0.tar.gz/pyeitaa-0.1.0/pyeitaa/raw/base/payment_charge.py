from typing import Union
from pyeitaa import raw

PaymentCharge = Union[raw.types.PaymentCharge]


# noinspection PyRedeclaration
class PaymentCharge:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PaymentCharge <pyeitaa.raw.types.PaymentCharge>`
    """

    QUALNAME = "pyeitaa.raw.base.PaymentCharge"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
