from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class RequestCall(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x42ff96ed``

    Parameters:
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        random_id: ``int`` ``32-bit``
        g_a_hash: ``bytes``
        protocol: :obj:`PhoneCallProtocol <pyeitaa.raw.base.PhoneCallProtocol>`
        video (optional): ``bool``

    Returns:
        :obj:`phone.PhoneCall <pyeitaa.raw.base.phone.PhoneCall>`
    """

    __slots__: List[str] = ["user_id", "random_id", "g_a_hash", "protocol", "video"]

    ID = 0x42ff96ed
    QUALNAME = "functions.phone.RequestCall"

    def __init__(self, *, user_id: "raw.base.InputUser", random_id: int, g_a_hash: bytes, protocol: "raw.base.PhoneCallProtocol", video: Optional[bool] = None) -> None:
        self.user_id = user_id  # InputUser
        self.random_id = random_id  # int
        self.g_a_hash = g_a_hash  # bytes
        self.protocol = protocol  # PhoneCallProtocol
        self.video = video  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        video = True if flags & (1 << 0) else False
        user_id = TLObject.read(data)
        
        random_id = Int.read(data)
        
        g_a_hash = Bytes.read(data)
        
        protocol = TLObject.read(data)
        
        return RequestCall(user_id=user_id, random_id=random_id, g_a_hash=g_a_hash, protocol=protocol, video=video)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.video else 0
        data.write(Int(flags))
        
        data.write(self.user_id.write())
        
        data.write(Int(self.random_id))
        
        data.write(Bytes(self.g_a_hash))
        
        data.write(self.protocol.write())
        
        return data.getvalue()
