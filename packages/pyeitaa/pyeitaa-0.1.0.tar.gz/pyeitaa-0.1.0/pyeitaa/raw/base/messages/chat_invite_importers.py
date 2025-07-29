from typing import Union
from pyeitaa import raw

ChatInviteImporters = Union[raw.types.messages.ChatInviteImporters]


# noinspection PyRedeclaration
class ChatInviteImporters:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.ChatInviteImporters <pyeitaa.raw.types.messages.ChatInviteImporters>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetChatInviteImporters <pyeitaa.raw.functions.messages.GetChatInviteImporters>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.ChatInviteImporters"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
