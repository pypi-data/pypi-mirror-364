from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ChatInviteLayer84(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatInvite`.

    Details:
        - Layer: ``135``
        - ID: ``-0x248b0aa8``

    Parameters:
        title: ``str``
        photo: :obj:`ChatPhoto <pyeitaa.raw.base.ChatPhoto>`
        participants_count: ``int`` ``32-bit``
        channel (optional): ``bool``
        broadcast (optional): ``bool``
        public (optional): ``bool``
        megagroup (optional): ``bool``
        participants (optional): List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.CheckChatInvite <pyeitaa.raw.functions.messages.CheckChatInvite>`
    """

    __slots__: List[str] = ["title", "photo", "participants_count", "channel", "broadcast", "public", "megagroup", "participants"]

    ID = -0x248b0aa8
    QUALNAME = "types.ChatInviteLayer84"

    def __init__(self, *, title: str, photo: "raw.base.ChatPhoto", participants_count: int, channel: Optional[bool] = None, broadcast: Optional[bool] = None, public: Optional[bool] = None, megagroup: Optional[bool] = None, participants: Optional[List["raw.base.User"]] = None) -> None:
        self.title = title  # string
        self.photo = photo  # ChatPhoto
        self.participants_count = participants_count  # int
        self.channel = channel  # flags.0?true
        self.broadcast = broadcast  # flags.1?true
        self.public = public  # flags.2?true
        self.megagroup = megagroup  # flags.3?true
        self.participants = participants  # flags.4?Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        channel = True if flags & (1 << 0) else False
        broadcast = True if flags & (1 << 1) else False
        public = True if flags & (1 << 2) else False
        megagroup = True if flags & (1 << 3) else False
        title = String.read(data)
        
        photo = TLObject.read(data)
        
        participants_count = Int.read(data)
        
        participants = TLObject.read(data) if flags & (1 << 4) else []
        
        return ChatInviteLayer84(title=title, photo=photo, participants_count=participants_count, channel=channel, broadcast=broadcast, public=public, megagroup=megagroup, participants=participants)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.channel else 0
        flags |= (1 << 1) if self.broadcast else 0
        flags |= (1 << 2) if self.public else 0
        flags |= (1 << 3) if self.megagroup else 0
        flags |= (1 << 4) if self.participants is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.title))
        
        data.write(self.photo.write())
        
        data.write(Int(self.participants_count))
        
        if self.participants is not None:
            data.write(Vector(self.participants))
        
        return data.getvalue()
