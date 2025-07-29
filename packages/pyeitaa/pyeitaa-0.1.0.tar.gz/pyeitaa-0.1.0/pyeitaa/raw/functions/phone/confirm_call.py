from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ConfirmCall(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x2efe1722``

    Parameters:
        peer: :obj:`InputPhoneCall <pyeitaa.raw.base.InputPhoneCall>`
        g_a: ``bytes``
        key_fingerprint: ``int`` ``64-bit``
        protocol: :obj:`PhoneCallProtocol <pyeitaa.raw.base.PhoneCallProtocol>`

    Returns:
        :obj:`phone.PhoneCall <pyeitaa.raw.base.phone.PhoneCall>`
    """

    __slots__: List[str] = ["peer", "g_a", "key_fingerprint", "protocol"]

    ID = 0x2efe1722
    QUALNAME = "functions.phone.ConfirmCall"

    def __init__(self, *, peer: "raw.base.InputPhoneCall", g_a: bytes, key_fingerprint: int, protocol: "raw.base.PhoneCallProtocol") -> None:
        self.peer = peer  # InputPhoneCall
        self.g_a = g_a  # bytes
        self.key_fingerprint = key_fingerprint  # long
        self.protocol = protocol  # PhoneCallProtocol

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        g_a = Bytes.read(data)
        
        key_fingerprint = Long.read(data)
        
        protocol = TLObject.read(data)
        
        return ConfirmCall(peer=peer, g_a=g_a, key_fingerprint=key_fingerprint, protocol=protocol)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Bytes(self.g_a))
        
        data.write(Long(self.key_fingerprint))
        
        data.write(self.protocol.write())
        
        return data.getvalue()
