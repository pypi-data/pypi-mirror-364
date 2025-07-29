from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PhoneCall(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PhoneCall`.

    Details:
        - Layer: ``135``
        - ID: ``-0x69808399``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
        admin_id: ``int`` ``64-bit``
        participant_id: ``int`` ``64-bit``
        g_a_or_b: ``bytes``
        key_fingerprint: ``int`` ``64-bit``
        protocol: :obj:`PhoneCallProtocol <pyeitaa.raw.base.PhoneCallProtocol>`
        connections: List of :obj:`PhoneConnection <pyeitaa.raw.base.PhoneConnection>`
        start_date: ``int`` ``32-bit``
        p2p_allowed (optional): ``bool``
        video (optional): ``bool``
    """

    __slots__: List[str] = ["id", "access_hash", "date", "admin_id", "participant_id", "g_a_or_b", "key_fingerprint", "protocol", "connections", "start_date", "p2p_allowed", "video"]

    ID = -0x69808399
    QUALNAME = "types.PhoneCall"

    def __init__(self, *, id: int, access_hash: int, date: int, admin_id: int, participant_id: int, g_a_or_b: bytes, key_fingerprint: int, protocol: "raw.base.PhoneCallProtocol", connections: List["raw.base.PhoneConnection"], start_date: int, p2p_allowed: Optional[bool] = None, video: Optional[bool] = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.date = date  # int
        self.admin_id = admin_id  # long
        self.participant_id = participant_id  # long
        self.g_a_or_b = g_a_or_b  # bytes
        self.key_fingerprint = key_fingerprint  # long
        self.protocol = protocol  # PhoneCallProtocol
        self.connections = connections  # Vector<PhoneConnection>
        self.start_date = start_date  # int
        self.p2p_allowed = p2p_allowed  # flags.5?true
        self.video = video  # flags.6?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        p2p_allowed = True if flags & (1 << 5) else False
        video = True if flags & (1 << 6) else False
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        date = Int.read(data)
        
        admin_id = Long.read(data)
        
        participant_id = Long.read(data)
        
        g_a_or_b = Bytes.read(data)
        
        key_fingerprint = Long.read(data)
        
        protocol = TLObject.read(data)
        
        connections = TLObject.read(data)
        
        start_date = Int.read(data)
        
        return PhoneCall(id=id, access_hash=access_hash, date=date, admin_id=admin_id, participant_id=participant_id, g_a_or_b=g_a_or_b, key_fingerprint=key_fingerprint, protocol=protocol, connections=connections, start_date=start_date, p2p_allowed=p2p_allowed, video=video)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 5) if self.p2p_allowed else 0
        flags |= (1 << 6) if self.video else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Int(self.date))
        
        data.write(Long(self.admin_id))
        
        data.write(Long(self.participant_id))
        
        data.write(Bytes(self.g_a_or_b))
        
        data.write(Long(self.key_fingerprint))
        
        data.write(self.protocol.write())
        
        data.write(Vector(self.connections))
        
        data.write(Int(self.start_date))
        
        return data.getvalue()
