from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AcceptEncryption(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3dbc0415``

    Parameters:
        peer: :obj:`InputEncryptedChat <pyeitaa.raw.base.InputEncryptedChat>`
        g_b: ``bytes``
        key_fingerprint: ``int`` ``64-bit``

    Returns:
        :obj:`EncryptedChat <pyeitaa.raw.base.EncryptedChat>`
    """

    __slots__: List[str] = ["peer", "g_b", "key_fingerprint"]

    ID = 0x3dbc0415
    QUALNAME = "functions.messages.AcceptEncryption"

    def __init__(self, *, peer: "raw.base.InputEncryptedChat", g_b: bytes, key_fingerprint: int) -> None:
        self.peer = peer  # InputEncryptedChat
        self.g_b = g_b  # bytes
        self.key_fingerprint = key_fingerprint  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        g_b = Bytes.read(data)
        
        key_fingerprint = Long.read(data)
        
        return AcceptEncryption(peer=peer, g_b=g_b, key_fingerprint=key_fingerprint)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Bytes(self.g_b))
        
        data.write(Long(self.key_fingerprint))
        
        return data.getvalue()
