from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SaveBigFilePart(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x218498c3``

    Parameters:
        file_id: ``int`` ``64-bit``
        file_part: ``int`` ``32-bit``
        file_total_parts: ``int`` ``32-bit``
        bytes: ``bytes``
        peer (optional): :obj:`Peer <pyeitaa.raw.base.Peer>`
        totalFileSize (optional): ``int`` ``64-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["file_id", "file_part", "file_total_parts", "bytes", "peer", "totalFileSize"]

    ID = -0x218498c3
    QUALNAME = "functions.upload.SaveBigFilePart"

    def __init__(self, *, file_id: int, file_part: int, file_total_parts: int, bytes: bytes, peer: "raw.base.Peer" = None, totalFileSize: Optional[int] = None) -> None:
        self.file_id = file_id  # long
        self.file_part = file_part  # int
        self.file_total_parts = file_total_parts  # int
        self.bytes = bytes  # bytes
        self.peer = peer  # flags.0?Peer
        self.totalFileSize = totalFileSize  # flags.1?long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        
        file_id = Long.read(data)
        
        file_part = Int.read(data)
        
        file_total_parts = Int.read(data)
        
        bytes = Bytes.read(data)
        flags = Int.read(data)
        
        peer = TLObject.read(data) if flags & (1 << 0) else None
        
        totalFileSize = Long.read(data) if flags & (1 << 1) else None
        return SaveBigFilePart(file_id=file_id, file_part=file_part, file_total_parts=file_total_parts, bytes=bytes, peer=peer, totalFileSize=totalFileSize)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        
        data.write(Long(self.file_id))
        
        data.write(Int(self.file_part))
        
        data.write(Int(self.file_total_parts))
        
        data.write(Bytes(self.bytes))
        flags = 0
        flags |= (1 << 0) if self.peer is not None else 0
        flags |= (1 << 1) if self.totalFileSize is not None else 0
        data.write(Int(flags))
        
        if self.peer is not None:
            data.write(self.peer.write())
        
        if self.totalFileSize is not None:
            data.write(Long(self.totalFileSize))
        
        return data.getvalue()
