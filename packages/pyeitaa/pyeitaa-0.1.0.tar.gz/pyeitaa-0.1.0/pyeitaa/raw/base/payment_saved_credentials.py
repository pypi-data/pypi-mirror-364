from typing import Union
from pyeitaa import raw

PaymentSavedCredentials = Union[raw.types.PaymentSavedCredentialsCard]


# noinspection PyRedeclaration
class PaymentSavedCredentials:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PaymentSavedCredentialsCard <pyeitaa.raw.types.PaymentSavedCredentialsCard>`
    """

    QUALNAME = "pyeitaa.raw.base.PaymentSavedCredentials"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
