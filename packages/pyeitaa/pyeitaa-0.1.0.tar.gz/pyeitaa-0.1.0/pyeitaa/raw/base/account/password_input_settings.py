from typing import Union
from pyeitaa import raw

PasswordInputSettings = Union[raw.types.account.PasswordInputSettings, raw.types.account.PasswordInputSettingsLayer68]


# noinspection PyRedeclaration
class PasswordInputSettings:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.PasswordInputSettings <pyeitaa.raw.types.account.PasswordInputSettings>`
            - :obj:`account.PasswordInputSettingsLayer68 <pyeitaa.raw.types.account.PasswordInputSettingsLayer68>`
    """

    QUALNAME = "pyeitaa.raw.base.account.PasswordInputSettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
