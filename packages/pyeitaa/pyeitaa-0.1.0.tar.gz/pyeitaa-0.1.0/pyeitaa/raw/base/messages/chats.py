from typing import Union
from pyeitaa import raw

Chats = Union[raw.types.messages.Chats, raw.types.messages.ChatsSlice]


# noinspection PyRedeclaration
class Chats:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.Chats <pyeitaa.raw.types.messages.Chats>`
            - :obj:`messages.ChatsSlice <pyeitaa.raw.types.messages.ChatsSlice>`

    See Also:
        This object can be returned by 7 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetChats <pyeitaa.raw.functions.messages.GetChats>`
            - :obj:`messages.GetCommonChats <pyeitaa.raw.functions.messages.GetCommonChats>`
            - :obj:`messages.GetAllChats <pyeitaa.raw.functions.messages.GetAllChats>`
            - :obj:`channels.GetChannels <pyeitaa.raw.functions.channels.GetChannels>`
            - :obj:`channels.GetAdminedPublicChannels <pyeitaa.raw.functions.channels.GetAdminedPublicChannels>`
            - :obj:`channels.GetLeftChannels <pyeitaa.raw.functions.channels.GetLeftChannels>`
            - :obj:`channels.GetGroupsForDiscussion <pyeitaa.raw.functions.channels.GetGroupsForDiscussion>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.Chats"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
