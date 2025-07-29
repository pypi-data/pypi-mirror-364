from typing import Union
from pyeitaa import raw

BadMsgNotification = Union[raw.types.BadMsgNotification, raw.types.BadMsgNotification, raw.types.BadServerSalt, raw.types.BadServerSalt]


# noinspection PyRedeclaration
class BadMsgNotification:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`BadMsgNotification <pyeitaa.raw.types.BadMsgNotification>`
            - :obj:`BadMsgNotification <pyeitaa.raw.types.BadMsgNotification>`
            - :obj:`BadServerSalt <pyeitaa.raw.types.BadServerSalt>`
            - :obj:`BadServerSalt <pyeitaa.raw.types.BadServerSalt>`
    """

    QUALNAME = "pyeitaa.raw.base.BadMsgNotification"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
