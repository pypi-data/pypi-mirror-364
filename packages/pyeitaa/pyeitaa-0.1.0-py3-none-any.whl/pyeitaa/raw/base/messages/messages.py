from typing import Union
from pyeitaa import raw

Messages = Union[raw.types.messages.ChannelMessages, raw.types.messages.Messages, raw.types.messages.MessagesNotModified, raw.types.messages.MessagesSlice]


# noinspection PyRedeclaration
class Messages:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.ChannelMessages <pyeitaa.raw.types.messages.ChannelMessages>`
            - :obj:`messages.Messages <pyeitaa.raw.types.messages.Messages>`
            - :obj:`messages.MessagesNotModified <pyeitaa.raw.types.messages.MessagesNotModified>`
            - :obj:`messages.MessagesSlice <pyeitaa.raw.types.messages.MessagesSlice>`

    See Also:
        This object can be returned by 12 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetMessages <pyeitaa.raw.functions.messages.GetMessages>`
            - :obj:`messages.GetHistory <pyeitaa.raw.functions.messages.GetHistory>`
            - :obj:`messages.Search <pyeitaa.raw.functions.messages.Search>`
            - :obj:`messages.SearchGlobal <pyeitaa.raw.functions.messages.SearchGlobal>`
            - :obj:`messages.SearchGlobalExt <pyeitaa.raw.functions.messages.SearchGlobalExt>`
            - :obj:`messages.GetUnreadMentions <pyeitaa.raw.functions.messages.GetUnreadMentions>`
            - :obj:`messages.GetRecentLocations <pyeitaa.raw.functions.messages.GetRecentLocations>`
            - :obj:`messages.GetScheduledHistory <pyeitaa.raw.functions.messages.GetScheduledHistory>`
            - :obj:`messages.GetScheduledMessages <pyeitaa.raw.functions.messages.GetScheduledMessages>`
            - :obj:`messages.GetReplies <pyeitaa.raw.functions.messages.GetReplies>`
            - :obj:`channels.GetMessages <pyeitaa.raw.functions.channels.GetMessages>`
            - :obj:`stats.GetMessagePublicForwards <pyeitaa.raw.functions.stats.GetMessagePublicForwards>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.Messages"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
