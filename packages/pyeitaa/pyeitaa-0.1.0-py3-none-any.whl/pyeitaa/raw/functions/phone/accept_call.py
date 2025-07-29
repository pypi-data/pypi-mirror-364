from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AcceptCall(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3bd2b4a0``

    Parameters:
        peer: :obj:`InputPhoneCall <pyeitaa.raw.base.InputPhoneCall>`
        g_b: ``bytes``
        protocol: :obj:`PhoneCallProtocol <pyeitaa.raw.base.PhoneCallProtocol>`

    Returns:
        :obj:`phone.PhoneCall <pyeitaa.raw.base.phone.PhoneCall>`
    """

    __slots__: List[str] = ["peer", "g_b", "protocol"]

    ID = 0x3bd2b4a0
    QUALNAME = "functions.phone.AcceptCall"

    def __init__(self, *, peer: "raw.base.InputPhoneCall", g_b: bytes, protocol: "raw.base.PhoneCallProtocol") -> None:
        self.peer = peer  # InputPhoneCall
        self.g_b = g_b  # bytes
        self.protocol = protocol  # PhoneCallProtocol

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        g_b = Bytes.read(data)
        
        protocol = TLObject.read(data)
        
        return AcceptCall(peer=peer, g_b=g_b, protocol=protocol)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Bytes(self.g_b))
        
        data.write(self.protocol.write())
        
        return data.getvalue()
