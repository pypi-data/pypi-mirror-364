from typing import Union
from pyeitaa import raw

PaymentForm = Union[raw.types.payments.PaymentForm]


# noinspection PyRedeclaration
class PaymentForm:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`payments.PaymentForm <pyeitaa.raw.types.payments.PaymentForm>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.GetPaymentForm <pyeitaa.raw.functions.payments.GetPaymentForm>`
    """

    QUALNAME = "pyeitaa.raw.base.payments.PaymentForm"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
