from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class GetPasswordLayer68(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0xd74ad174``

    Parameters:
        phone_code (optional): ``str``
        phone_number (optional): ``str``

    Returns:
        :obj:`account.Password <pyeitaa.raw.base.account.Password>`
    """

    __slots__: List[str] = ["phone_code", "phone_number"]

    ID = 0xd74ad174
    QUALNAME = "functions.account.GetPasswordLayer68"

    def __init__(self, *, phone_code: Optional[str] = None, phone_number: Optional[str] = None) -> None:
        self.phone_code = phone_code  # flags.0?string
        self.phone_number = phone_number  # flags.1?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        phone_code = String.read(data) if flags & (1 << 0) else None
        phone_number = String.read(data) if flags & (1 << 1) else None
        return GetPasswordLayer68(phone_code=phone_code, phone_number=phone_number)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.phone_code is not None else 0
        flags |= (1 << 1) if self.phone_number is not None else 0
        data.write(Int(flags))
        
        if self.phone_code is not None:
            data.write(String(self.phone_code))
        
        if self.phone_number is not None:
            data.write(String(self.phone_number))
        
        return data.getvalue()
