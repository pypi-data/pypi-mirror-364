from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class BindAuthKeyInner(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.BindAuthKeyInner`.

    Details:
        - Layer: ``135``
        - ID: ``0x75a3f765``

    Parameters:
        nonce: ``int`` ``64-bit``
        temp_auth_key_id: ``int`` ``64-bit``
        perm_auth_key_id: ``int`` ``64-bit``
        temp_session_id: ``int`` ``64-bit``
        expires_at: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["nonce", "temp_auth_key_id", "perm_auth_key_id", "temp_session_id", "expires_at"]

    ID = 0x75a3f765
    QUALNAME = "types.BindAuthKeyInner"

    def __init__(self, *, nonce: int, temp_auth_key_id: int, perm_auth_key_id: int, temp_session_id: int, expires_at: int) -> None:
        self.nonce = nonce  # long
        self.temp_auth_key_id = temp_auth_key_id  # long
        self.perm_auth_key_id = perm_auth_key_id  # long
        self.temp_session_id = temp_session_id  # long
        self.expires_at = expires_at  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        nonce = Long.read(data)
        
        temp_auth_key_id = Long.read(data)
        
        perm_auth_key_id = Long.read(data)
        
        temp_session_id = Long.read(data)
        
        expires_at = Int.read(data)
        
        return BindAuthKeyInner(nonce=nonce, temp_auth_key_id=temp_auth_key_id, perm_auth_key_id=perm_auth_key_id, temp_session_id=temp_session_id, expires_at=expires_at)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.nonce))
        
        data.write(Long(self.temp_auth_key_id))
        
        data.write(Long(self.perm_auth_key_id))
        
        data.write(Long(self.temp_session_id))
        
        data.write(Int(self.expires_at))
        
        return data.getvalue()
