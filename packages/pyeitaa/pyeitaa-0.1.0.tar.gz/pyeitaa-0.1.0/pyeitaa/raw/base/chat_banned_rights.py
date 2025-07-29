from typing import Union
from pyeitaa import raw

ChatBannedRights = Union[raw.types.ChatBannedRights]


# noinspection PyRedeclaration
class ChatBannedRights:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChatBannedRights <pyeitaa.raw.types.ChatBannedRights>`
    """

    QUALNAME = "pyeitaa.raw.base.ChatBannedRights"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
