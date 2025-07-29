from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class StartHistoryImport(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4bc20cbc``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        import_id: ``int`` ``64-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "import_id"]

    ID = -0x4bc20cbc
    QUALNAME = "functions.messages.StartHistoryImport"

    def __init__(self, *, peer: "raw.base.InputPeer", import_id: int) -> None:
        self.peer = peer  # InputPeer
        self.import_id = import_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        import_id = Long.read(data)
        
        return StartHistoryImport(peer=peer, import_id=import_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Long(self.import_id))
        
        return data.getvalue()
