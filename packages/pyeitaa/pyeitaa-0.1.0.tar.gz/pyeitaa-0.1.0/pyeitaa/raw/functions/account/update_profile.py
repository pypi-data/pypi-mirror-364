from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class UpdateProfile(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x78515775``

    Parameters:
        first_name (optional): ``str``
        last_name (optional): ``str``
        about (optional): ``str``

    Returns:
        :obj:`User <pyeitaa.raw.base.User>`
    """

    __slots__: List[str] = ["first_name", "last_name", "about"]

    ID = 0x78515775
    QUALNAME = "functions.account.UpdateProfile"

    def __init__(self, *, first_name: Optional[str] = None, last_name: Optional[str] = None, about: Optional[str] = None) -> None:
        self.first_name = first_name  # flags.0?string
        self.last_name = last_name  # flags.1?string
        self.about = about  # flags.2?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        first_name = String.read(data) if flags & (1 << 0) else None
        last_name = String.read(data) if flags & (1 << 1) else None
        about = String.read(data) if flags & (1 << 2) else None
        return UpdateProfile(first_name=first_name, last_name=last_name, about=about)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.first_name is not None else 0
        flags |= (1 << 1) if self.last_name is not None else 0
        flags |= (1 << 2) if self.about is not None else 0
        data.write(Int(flags))
        
        if self.first_name is not None:
            data.write(String(self.first_name))
        
        if self.last_name is not None:
            data.write(String(self.last_name))
        
        if self.about is not None:
            data.write(String(self.about))
        
        return data.getvalue()
