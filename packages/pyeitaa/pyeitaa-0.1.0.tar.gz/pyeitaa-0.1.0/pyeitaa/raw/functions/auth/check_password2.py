from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class CheckPassword2(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x767425e1``

    Parameters:
        password_hash: ``bytes``
        phone_code (optional): ``str``
        phone_number (optional): ``str``

    Returns:
        :obj:`auth.Authorization <pyeitaa.raw.base.auth.Authorization>`
    """

    __slots__: List[str] = ["password_hash", "phone_code", "phone_number"]

    ID = -0x767425e1
    QUALNAME = "functions.auth.CheckPassword2"

    def __init__(self, *, password_hash: bytes, phone_code: Optional[str] = None, phone_number: Optional[str] = None) -> None:
        self.password_hash = password_hash  # bytes
        self.phone_code = phone_code  # flags.0?string
        self.phone_number = phone_number  # flags.1?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        
        password_hash = Bytes.read(data)
        flags = Int.read(data)
        
        phone_code = String.read(data) if flags & (1 << 0) else None
        phone_number = String.read(data) if flags & (1 << 1) else None
        return CheckPassword2(password_hash=password_hash, phone_code=phone_code, phone_number=phone_number)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        
        data.write(Bytes(self.password_hash))
        flags = 0
        flags |= (1 << 0) if self.phone_code is not None else 0
        flags |= (1 << 1) if self.phone_number is not None else 0
        data.write(Int(flags))
        
        if self.phone_code is not None:
            data.write(String(self.phone_code))
        
        if self.phone_number is not None:
            data.write(String(self.phone_number))
        
        return data.getvalue()
