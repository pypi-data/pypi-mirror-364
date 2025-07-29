from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PhoneCallAccepted(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PhoneCall`.

    Details:
        - Layer: ``135``
        - ID: ``0x3660c311``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
        admin_id: ``int`` ``64-bit``
        participant_id: ``int`` ``64-bit``
        g_b: ``bytes``
        protocol: :obj:`PhoneCallProtocol <pyeitaa.raw.base.PhoneCallProtocol>`
        video (optional): ``bool``
    """

    __slots__: List[str] = ["id", "access_hash", "date", "admin_id", "participant_id", "g_b", "protocol", "video"]

    ID = 0x3660c311
    QUALNAME = "types.PhoneCallAccepted"

    def __init__(self, *, id: int, access_hash: int, date: int, admin_id: int, participant_id: int, g_b: bytes, protocol: "raw.base.PhoneCallProtocol", video: Optional[bool] = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.date = date  # int
        self.admin_id = admin_id  # long
        self.participant_id = participant_id  # long
        self.g_b = g_b  # bytes
        self.protocol = protocol  # PhoneCallProtocol
        self.video = video  # flags.6?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        video = True if flags & (1 << 6) else False
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        date = Int.read(data)
        
        admin_id = Long.read(data)
        
        participant_id = Long.read(data)
        
        g_b = Bytes.read(data)
        
        protocol = TLObject.read(data)
        
        return PhoneCallAccepted(id=id, access_hash=access_hash, date=date, admin_id=admin_id, participant_id=participant_id, g_b=g_b, protocol=protocol, video=video)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 6) if self.video else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Int(self.date))
        
        data.write(Long(self.admin_id))
        
        data.write(Long(self.participant_id))
        
        data.write(Bytes(self.g_b))
        
        data.write(self.protocol.write())
        
        return data.getvalue()
