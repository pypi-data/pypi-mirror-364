from typing import Union
from pyeitaa import raw

BankCardData = Union[raw.types.payments.BankCardData]


# noinspection PyRedeclaration
class BankCardData:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`payments.BankCardData <pyeitaa.raw.types.payments.BankCardData>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.GetBankCardData <pyeitaa.raw.functions.payments.GetBankCardData>`
    """

    QUALNAME = "pyeitaa.raw.base.payments.BankCardData"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
