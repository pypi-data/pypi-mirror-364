from typing import Union
from pyeitaa import raw

PaymentReceipt = Union[raw.types.payments.PaymentReceipt]


# noinspection PyRedeclaration
class PaymentReceipt:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`payments.PaymentReceipt <pyeitaa.raw.types.payments.PaymentReceipt>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.GetPaymentReceipt <pyeitaa.raw.functions.payments.GetPaymentReceipt>`
    """

    QUALNAME = "pyeitaa.raw.base.payments.PaymentReceipt"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
