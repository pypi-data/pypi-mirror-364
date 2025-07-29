from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ChannelMessages(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.Messages`.

    Details:
        - Layer: ``135``
        - ID: ``0x64479808``

    Parameters:
        pts: ``int`` ``32-bit``
        count: ``int`` ``32-bit``
        messages: List of :obj:`Message <pyeitaa.raw.base.Message>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`
        inexact (optional): ``bool``
        offset_id_offset (optional): ``int`` ``32-bit``

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

    __slots__: List[str] = ["pts", "count", "messages", "chats", "users", "inexact", "offset_id_offset"]

    ID = 0x64479808
    QUALNAME = "types.messages.ChannelMessages"

    def __init__(self, *, pts: int, count: int, messages: List["raw.base.Message"], chats: List["raw.base.Chat"], users: List["raw.base.User"], inexact: Optional[bool] = None, offset_id_offset: Optional[int] = None) -> None:
        self.pts = pts  # int
        self.count = count  # int
        self.messages = messages  # Vector<Message>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>
        self.inexact = inexact  # flags.1?true
        self.offset_id_offset = offset_id_offset  # flags.2?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        inexact = True if flags & (1 << 1) else False
        pts = Int.read(data)
        
        count = Int.read(data)
        
        offset_id_offset = Int.read(data) if flags & (1 << 2) else None
        messages = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return ChannelMessages(pts=pts, count=count, messages=messages, chats=chats, users=users, inexact=inexact, offset_id_offset=offset_id_offset)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.inexact else 0
        flags |= (1 << 2) if self.offset_id_offset is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.pts))
        
        data.write(Int(self.count))
        
        if self.offset_id_offset is not None:
            data.write(Int(self.offset_id_offset))
        
        data.write(Vector(self.messages))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
