from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetGroupParticipants(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x3aa72755``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        ids: List of :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        sources: List of ``int`` ``32-bit``
        offset: ``str``
        limit: ``int`` ``32-bit``

    Returns:
        :obj:`phone.GroupParticipants <pyeitaa.raw.base.phone.GroupParticipants>`
    """

    __slots__: List[str] = ["call", "ids", "sources", "offset", "limit"]

    ID = -0x3aa72755
    QUALNAME = "functions.phone.GetGroupParticipants"

    def __init__(self, *, call: "raw.base.InputGroupCall", ids: List["raw.base.InputPeer"], sources: List[int], offset: str, limit: int) -> None:
        self.call = call  # InputGroupCall
        self.ids = ids  # Vector<InputPeer>
        self.sources = sources  # Vector<int>
        self.offset = offset  # string
        self.limit = limit  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        call = TLObject.read(data)
        
        ids = TLObject.read(data)
        
        sources = TLObject.read(data, Int)
        
        offset = String.read(data)
        
        limit = Int.read(data)
        
        return GetGroupParticipants(call=call, ids=ids, sources=sources, offset=offset, limit=limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.call.write())
        
        data.write(Vector(self.ids))
        
        data.write(Vector(self.sources, Int))
        
        data.write(String(self.offset))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
