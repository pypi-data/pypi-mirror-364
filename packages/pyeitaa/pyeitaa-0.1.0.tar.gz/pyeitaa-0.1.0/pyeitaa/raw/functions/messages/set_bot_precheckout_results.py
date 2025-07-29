from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class SetBotPrecheckoutResults(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x9c2dd95``

    Parameters:
        query_id: ``int`` ``64-bit``
        success (optional): ``bool``
        error (optional): ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["query_id", "success", "error"]

    ID = 0x9c2dd95
    QUALNAME = "functions.messages.SetBotPrecheckoutResults"

    def __init__(self, *, query_id: int, success: Optional[bool] = None, error: Optional[str] = None) -> None:
        self.query_id = query_id  # long
        self.success = success  # flags.1?true
        self.error = error  # flags.0?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        success = True if flags & (1 << 1) else False
        query_id = Long.read(data)
        
        error = String.read(data) if flags & (1 << 0) else None
        return SetBotPrecheckoutResults(query_id=query_id, success=success, error=error)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.success else 0
        flags |= (1 << 0) if self.error is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.query_id))
        
        if self.error is not None:
            data.write(String(self.error))
        
        return data.getvalue()
