from typing import Union
from pyeitaa import raw

PaymentRequestedInfo = Union[raw.types.PaymentRequestedInfo]


# noinspection PyRedeclaration
class PaymentRequestedInfo:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PaymentRequestedInfo <pyeitaa.raw.types.PaymentRequestedInfo>`
    """

    QUALNAME = "pyeitaa.raw.base.PaymentRequestedInfo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
