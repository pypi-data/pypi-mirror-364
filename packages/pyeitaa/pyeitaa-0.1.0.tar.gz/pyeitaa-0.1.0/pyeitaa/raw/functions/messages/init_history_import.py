from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InitHistoryImport(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x34090c3b``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        file: :obj:`InputFile <pyeitaa.raw.base.InputFile>`
        media_count: ``int`` ``32-bit``

    Returns:
        :obj:`messages.HistoryImport <pyeitaa.raw.base.messages.HistoryImport>`
    """

    __slots__: List[str] = ["peer", "file", "media_count"]

    ID = 0x34090c3b
    QUALNAME = "functions.messages.InitHistoryImport"

    def __init__(self, *, peer: "raw.base.InputPeer", file: "raw.base.InputFile", media_count: int) -> None:
        self.peer = peer  # InputPeer
        self.file = file  # InputFile
        self.media_count = media_count  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        file = TLObject.read(data)
        
        media_count = Int.read(data)
        
        return InitHistoryImport(peer=peer, file=file, media_count=media_count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.file.write())
        
        data.write(Int(self.media_count))
        
        return data.getvalue()
