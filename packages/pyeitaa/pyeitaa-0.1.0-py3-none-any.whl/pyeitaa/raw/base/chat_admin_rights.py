from typing import Union
from pyeitaa import raw

ChatAdminRights = Union[raw.types.ChatAdminRights]


# noinspection PyRedeclaration
class ChatAdminRights:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChatAdminRights <pyeitaa.raw.types.ChatAdminRights>`
    """

    QUALNAME = "pyeitaa.raw.base.ChatAdminRights"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
