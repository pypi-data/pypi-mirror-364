from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessagesNotModified(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.Messages`.

    Details:
        - Layer: ``135``
        - ID: ``0x74535f21``

    Parameters:
        count: ``int`` ``32-bit``

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

    __slots__: List[str] = ["count"]

    ID = 0x74535f21
    QUALNAME = "types.messages.MessagesNotModified"

    def __init__(self, *, count: int) -> None:
        self.count = count  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        count = Int.read(data)
        
        return MessagesNotModified(count=count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.count))
        
        return data.getvalue()
