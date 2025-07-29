from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputPeerPhotoFileLocation(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputFileLocation`.

    Details:
        - Layer: ``135``
        - ID: ``0x37257e99``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        photo_id: ``int`` ``64-bit``
        volume_id: ``int`` ``64-bit``
        local_id: ``int`` ``32-bit``
        big (optional): ``bool``
    """

    __slots__: List[str] = ["peer", "photo_id", "volume_id", "local_id", "big"]

    ID = 0x37257e99
    QUALNAME = "types.InputPeerPhotoFileLocation"

    def __init__(self, *, peer: "raw.base.InputPeer", photo_id: int, volume_id: int, local_id: int, big: Optional[bool] = None) -> None:
        self.peer = peer  # InputPeer
        self.photo_id = photo_id  # long
        self.volume_id = volume_id  # long
        self.local_id = local_id  # int
        self.big = big  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        big = True if flags & (1 << 0) else False
        peer = TLObject.read(data)
        
        photo_id = Long.read(data)
        
        volume_id = Long.read(data)
        
        local_id = Int.read(data)
        
        return InputPeerPhotoFileLocation(peer=peer, photo_id=photo_id, volume_id=volume_id, local_id=local_id, big=big)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.big else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Long(self.photo_id))
        
        data.write(Long(self.volume_id))
        
        data.write(Int(self.local_id))
        
        return data.getvalue()
