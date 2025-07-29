from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GetPollVotes(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4791c7f2``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        id: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``
        option (optional): ``bytes``
        offset (optional): ``str``

    Returns:
        :obj:`messages.VotesList <pyeitaa.raw.base.messages.VotesList>`
    """

    __slots__: List[str] = ["peer", "id", "limit", "option", "offset"]

    ID = -0x4791c7f2
    QUALNAME = "functions.messages.GetPollVotes"

    def __init__(self, *, peer: "raw.base.InputPeer", id: int, limit: int, option: Optional[bytes] = None, offset: Optional[str] = None) -> None:
        self.peer = peer  # InputPeer
        self.id = id  # int
        self.limit = limit  # int
        self.option = option  # flags.0?bytes
        self.offset = offset  # flags.1?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        peer = TLObject.read(data)
        
        id = Int.read(data)
        
        option = Bytes.read(data) if flags & (1 << 0) else None
        offset = String.read(data) if flags & (1 << 1) else None
        limit = Int.read(data)
        
        return GetPollVotes(peer=peer, id=id, limit=limit, option=option, offset=offset)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.option is not None else 0
        flags |= (1 << 1) if self.offset is not None else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Int(self.id))
        
        if self.option is not None:
            data.write(Bytes(self.option))
        
        if self.offset is not None:
            data.write(String(self.offset))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
