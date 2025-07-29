from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PhoneCallWaiting(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PhoneCall`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3add90e9``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
        admin_id: ``int`` ``64-bit``
        participant_id: ``int`` ``64-bit``
        protocol: :obj:`PhoneCallProtocol <pyeitaa.raw.base.PhoneCallProtocol>`
        video (optional): ``bool``
        receive_date (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "access_hash", "date", "admin_id", "participant_id", "protocol", "video", "receive_date"]

    ID = -0x3add90e9
    QUALNAME = "types.PhoneCallWaiting"

    def __init__(self, *, id: int, access_hash: int, date: int, admin_id: int, participant_id: int, protocol: "raw.base.PhoneCallProtocol", video: Optional[bool] = None, receive_date: Optional[int] = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.date = date  # int
        self.admin_id = admin_id  # long
        self.participant_id = participant_id  # long
        self.protocol = protocol  # PhoneCallProtocol
        self.video = video  # flags.6?true
        self.receive_date = receive_date  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        video = True if flags & (1 << 6) else False
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        date = Int.read(data)
        
        admin_id = Long.read(data)
        
        participant_id = Long.read(data)
        
        protocol = TLObject.read(data)
        
        receive_date = Int.read(data) if flags & (1 << 0) else None
        return PhoneCallWaiting(id=id, access_hash=access_hash, date=date, admin_id=admin_id, participant_id=participant_id, protocol=protocol, video=video, receive_date=receive_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 6) if self.video else 0
        flags |= (1 << 0) if self.receive_date is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Int(self.date))
        
        data.write(Long(self.admin_id))
        
        data.write(Long(self.participant_id))
        
        data.write(self.protocol.write())
        
        if self.receive_date is not None:
            data.write(Int(self.receive_date))
        
        return data.getvalue()
