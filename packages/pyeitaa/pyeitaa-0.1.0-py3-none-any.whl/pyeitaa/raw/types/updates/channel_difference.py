from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ChannelDifference(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.updates.ChannelDifference`.

    Details:
        - Layer: ``135``
        - ID: ``0x2064674e``

    Parameters:
        pts: ``int`` ``32-bit``
        new_messages: List of :obj:`Message <pyeitaa.raw.base.Message>`
        other_updates: List of :obj:`Update <pyeitaa.raw.base.Update>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`
        final (optional): ``bool``
        timeout (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`updates.GetChannelDifference <pyeitaa.raw.functions.updates.GetChannelDifference>`
    """

    __slots__: List[str] = ["pts", "new_messages", "other_updates", "chats", "users", "final", "timeout"]

    ID = 0x2064674e
    QUALNAME = "types.updates.ChannelDifference"

    def __init__(self, *, pts: int, new_messages: List["raw.base.Message"], other_updates: List["raw.base.Update"], chats: List["raw.base.Chat"], users: List["raw.base.User"], final: Optional[bool] = None, timeout: Optional[int] = None) -> None:
        self.pts = pts  # int
        self.new_messages = new_messages  # Vector<Message>
        self.other_updates = other_updates  # Vector<Update>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>
        self.final = final  # flags.0?true
        self.timeout = timeout  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        final = True if flags & (1 << 0) else False
        pts = Int.read(data)
        
        timeout = Int.read(data) if flags & (1 << 1) else None
        new_messages = TLObject.read(data)
        
        other_updates = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return ChannelDifference(pts=pts, new_messages=new_messages, other_updates=other_updates, chats=chats, users=users, final=final, timeout=timeout)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.final else 0
        flags |= (1 << 1) if self.timeout is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.pts))
        
        if self.timeout is not None:
            data.write(Int(self.timeout))
        
        data.write(Vector(self.new_messages))
        
        data.write(Vector(self.other_updates))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
