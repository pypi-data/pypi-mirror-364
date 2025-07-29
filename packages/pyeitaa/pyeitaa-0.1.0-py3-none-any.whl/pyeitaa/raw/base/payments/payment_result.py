from typing import Union
from pyeitaa import raw

PaymentResult = Union[raw.types.payments.PaymentResult, raw.types.payments.PaymentVerificationNeeded]


# noinspection PyRedeclaration
class PaymentResult:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`payments.PaymentResult <pyeitaa.raw.types.payments.PaymentResult>`
            - :obj:`payments.PaymentVerificationNeeded <pyeitaa.raw.types.payments.PaymentVerificationNeeded>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.SendPaymentForm <pyeitaa.raw.functions.payments.SendPaymentForm>`
    """

    QUALNAME = "pyeitaa.raw.base.payments.PaymentResult"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
