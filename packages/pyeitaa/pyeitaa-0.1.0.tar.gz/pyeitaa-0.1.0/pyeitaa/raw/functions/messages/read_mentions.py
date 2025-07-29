from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ReadMentions(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0xf0189d3``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`

    Returns:
        :obj:`messages.AffectedHistory <pyeitaa.raw.base.messages.AffectedHistory>`
    """

    __slots__: List[str] = ["peer"]

    ID = 0xf0189d3
    QUALNAME = "functions.messages.ReadMentions"

    def __init__(self, *, peer: "raw.base.InputPeer") -> None:
        self.peer = peer  # InputPeer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        return ReadMentions(peer=peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        return data.getvalue()
