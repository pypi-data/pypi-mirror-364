from typing import Union
from pyeitaa import raw

InputPaymentCredentials = Union[raw.types.InputPaymentCredentials, raw.types.InputPaymentCredentialsApplePay, raw.types.InputPaymentCredentialsGooglePay, raw.types.InputPaymentCredentialsSaved]


# noinspection PyRedeclaration
class InputPaymentCredentials:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputPaymentCredentials <pyeitaa.raw.types.InputPaymentCredentials>`
            - :obj:`InputPaymentCredentialsApplePay <pyeitaa.raw.types.InputPaymentCredentialsApplePay>`
            - :obj:`InputPaymentCredentialsGooglePay <pyeitaa.raw.types.InputPaymentCredentialsGooglePay>`
            - :obj:`InputPaymentCredentialsSaved <pyeitaa.raw.types.InputPaymentCredentialsSaved>`
    """

    QUALNAME = "pyeitaa.raw.base.InputPaymentCredentials"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
