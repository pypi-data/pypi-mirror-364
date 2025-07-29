from typing import Union
from pyeitaa import raw

ChatInviteImporter = Union[raw.types.ChatInviteImporter]


# noinspection PyRedeclaration
class ChatInviteImporter:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChatInviteImporter <pyeitaa.raw.types.ChatInviteImporter>`
    """

    QUALNAME = "pyeitaa.raw.base.ChatInviteImporter"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
