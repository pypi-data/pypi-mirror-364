from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetMessageEditData(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x25972ca``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        id: ``int`` ``32-bit``

    Returns:
        :obj:`messages.MessageEditData <pyeitaa.raw.base.messages.MessageEditData>`
    """

    __slots__: List[str] = ["peer", "id"]

    ID = -0x25972ca
    QUALNAME = "functions.messages.GetMessageEditData"

    def __init__(self, *, peer: "raw.base.InputPeer", id: int) -> None:
        self.peer = peer  # InputPeer
        self.id = id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        id = Int.read(data)
        
        return GetMessageEditData(peer=peer, id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.id))
        
        return data.getvalue()
