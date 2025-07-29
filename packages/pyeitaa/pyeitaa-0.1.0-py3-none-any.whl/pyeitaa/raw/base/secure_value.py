from typing import Union
from pyeitaa import raw

SecureValue = Union[raw.types.SecureValue]


# noinspection PyRedeclaration
class SecureValue:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SecureValue <pyeitaa.raw.types.SecureValue>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetAllSecureValues <pyeitaa.raw.functions.account.GetAllSecureValues>`
            - :obj:`account.GetSecureValue <pyeitaa.raw.functions.account.GetSecureValue>`
            - :obj:`account.SaveSecureValue <pyeitaa.raw.functions.account.SaveSecureValue>`
    """

    QUALNAME = "pyeitaa.raw.base.SecureValue"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
