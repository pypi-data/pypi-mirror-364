from typing import Union
from pyeitaa import raw

UserStatus = Union[raw.types.UserStatusEmpty, raw.types.UserStatusLastMonth, raw.types.UserStatusLastWeek, raw.types.UserStatusOffline, raw.types.UserStatusOnline, raw.types.UserStatusRecently]


# noinspection PyRedeclaration
class UserStatus:
    """This base type has 6 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`UserStatusEmpty <pyeitaa.raw.types.UserStatusEmpty>`
            - :obj:`UserStatusLastMonth <pyeitaa.raw.types.UserStatusLastMonth>`
            - :obj:`UserStatusLastWeek <pyeitaa.raw.types.UserStatusLastWeek>`
            - :obj:`UserStatusOffline <pyeitaa.raw.types.UserStatusOffline>`
            - :obj:`UserStatusOnline <pyeitaa.raw.types.UserStatusOnline>`
            - :obj:`UserStatusRecently <pyeitaa.raw.types.UserStatusRecently>`
    """

    QUALNAME = "pyeitaa.raw.base.UserStatus"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
