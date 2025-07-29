from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bool, Bytes, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class RegisterDevice(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x1379fe86``

    Parameters:
        token_type: ``int`` ``32-bit``
        token: ``str``
        app_sandbox: ``bool``
        secret: ``bytes``
        other_uids: List of ``int`` ``64-bit``
        no_muted (optional): ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["token_type", "token", "app_sandbox", "secret", "other_uids", "no_muted"]

    ID = -0x1379fe86
    QUALNAME = "functions.account.RegisterDevice"

    def __init__(self, *, token_type: int, token: str, app_sandbox: bool, secret: bytes, other_uids: List[int], no_muted: Optional[bool] = None) -> None:
        self.token_type = token_type  # int
        self.token = token  # string
        self.app_sandbox = app_sandbox  # Bool
        self.secret = secret  # bytes
        self.other_uids = other_uids  # Vector<long>
        self.no_muted = no_muted  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        no_muted = True if flags & (1 << 0) else False
        token_type = Int.read(data)
        
        token = String.read(data)
        
        app_sandbox = Bool.read(data)
        
        secret = Bytes.read(data)
        
        other_uids = TLObject.read(data, Long)
        
        return RegisterDevice(token_type=token_type, token=token, app_sandbox=app_sandbox, secret=secret, other_uids=other_uids, no_muted=no_muted)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.no_muted else 0
        data.write(Int(flags))
        
        data.write(Int(self.token_type))
        
        data.write(String(self.token))
        
        data.write(Bool(self.app_sandbox))
        
        data.write(Bytes(self.secret))
        
        data.write(Vector(self.other_uids, Long))
        
        return data.getvalue()
