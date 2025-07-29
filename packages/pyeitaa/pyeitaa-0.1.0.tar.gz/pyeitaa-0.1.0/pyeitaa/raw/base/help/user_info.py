from typing import Union
from pyeitaa import raw

UserInfo = Union[raw.types.help.UserInfo, raw.types.help.UserInfoEmpty]


# noinspection PyRedeclaration
class UserInfo:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.UserInfo <pyeitaa.raw.types.help.UserInfo>`
            - :obj:`help.UserInfoEmpty <pyeitaa.raw.types.help.UserInfoEmpty>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`help.GetUserInfo <pyeitaa.raw.functions.help.GetUserInfo>`
            - :obj:`help.EditUserInfo <pyeitaa.raw.functions.help.EditUserInfo>`
    """

    QUALNAME = "pyeitaa.raw.base.help.UserInfo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
