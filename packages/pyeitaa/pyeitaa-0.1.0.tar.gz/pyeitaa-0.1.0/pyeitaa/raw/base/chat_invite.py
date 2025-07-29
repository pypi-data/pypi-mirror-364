from typing import Union
from pyeitaa import raw

ChatInvite = Union[raw.types.ChatInvite, raw.types.ChatInviteAlready, raw.types.ChatInviteLayer84, raw.types.ChatInvitePeek]


# noinspection PyRedeclaration
class ChatInvite:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChatInvite <pyeitaa.raw.types.ChatInvite>`
            - :obj:`ChatInviteAlready <pyeitaa.raw.types.ChatInviteAlready>`
            - :obj:`ChatInviteLayer84 <pyeitaa.raw.types.ChatInviteLayer84>`
            - :obj:`ChatInvitePeek <pyeitaa.raw.types.ChatInvitePeek>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.CheckChatInvite <pyeitaa.raw.functions.messages.CheckChatInvite>`
    """

    QUALNAME = "pyeitaa.raw.base.ChatInvite"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
