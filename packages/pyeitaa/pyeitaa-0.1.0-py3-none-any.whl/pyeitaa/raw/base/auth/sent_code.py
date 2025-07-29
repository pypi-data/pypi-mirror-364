from typing import Union
from pyeitaa import raw

SentCode = Union[raw.types.auth.SentCode]


# noinspection PyRedeclaration
class SentCode:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`auth.SentCode <pyeitaa.raw.types.auth.SentCode>`

    See Also:
        This object can be returned by 6 methods:

        .. hlist::
            :columns: 2

            - :obj:`auth.SendCode <pyeitaa.raw.functions.auth.SendCode>`
            - :obj:`auth.ResendCode <pyeitaa.raw.functions.auth.ResendCode>`
            - :obj:`account.SendChangePhoneCode <pyeitaa.raw.functions.account.SendChangePhoneCode>`
            - :obj:`account.SendConfirmPhoneCode <pyeitaa.raw.functions.account.SendConfirmPhoneCode>`
            - :obj:`account.SendVerifyPhoneCode <pyeitaa.raw.functions.account.SendVerifyPhoneCode>`
            - :obj:`SendTwoStepVerificationCode <pyeitaa.raw.functions.SendTwoStepVerificationCode>`
    """

    QUALNAME = "pyeitaa.raw.base.auth.SentCode"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
