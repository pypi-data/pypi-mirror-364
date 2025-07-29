from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class BindTempAuthKey(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x322bd5fb``

    Parameters:
        perm_auth_key_id: ``int`` ``64-bit``
        nonce: ``int`` ``64-bit``
        expires_at: ``int`` ``32-bit``
        encrypted_message: ``bytes``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["perm_auth_key_id", "nonce", "expires_at", "encrypted_message"]

    ID = -0x322bd5fb
    QUALNAME = "functions.auth.BindTempAuthKey"

    def __init__(self, *, perm_auth_key_id: int, nonce: int, expires_at: int, encrypted_message: bytes) -> None:
        self.perm_auth_key_id = perm_auth_key_id  # long
        self.nonce = nonce  # long
        self.expires_at = expires_at  # int
        self.encrypted_message = encrypted_message  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        perm_auth_key_id = Long.read(data)
        
        nonce = Long.read(data)
        
        expires_at = Int.read(data)
        
        encrypted_message = Bytes.read(data)
        
        return BindTempAuthKey(perm_auth_key_id=perm_auth_key_id, nonce=nonce, expires_at=expires_at, encrypted_message=encrypted_message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.perm_auth_key_id))
        
        data.write(Long(self.nonce))
        
        data.write(Int(self.expires_at))
        
        data.write(Bytes(self.encrypted_message))
        
        return data.getvalue()
