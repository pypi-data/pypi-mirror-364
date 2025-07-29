from typing import Union
from pyeitaa import raw

ResetPasswordResult = Union[raw.types.account.ResetPasswordFailedWait, raw.types.account.ResetPasswordOk, raw.types.account.ResetPasswordRequestedWait]


# noinspection PyRedeclaration
class ResetPasswordResult:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.ResetPasswordFailedWait <pyeitaa.raw.types.account.ResetPasswordFailedWait>`
            - :obj:`account.ResetPasswordOk <pyeitaa.raw.types.account.ResetPasswordOk>`
            - :obj:`account.ResetPasswordRequestedWait <pyeitaa.raw.types.account.ResetPasswordRequestedWait>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.ResetPassword <pyeitaa.raw.functions.account.ResetPassword>`
    """

    QUALNAME = "pyeitaa.raw.base.account.ResetPasswordResult"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
