from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class LoadAsyncGraph(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x621d5fa0``

    Parameters:
        token: ``str``
        x (optional): ``int`` ``64-bit``

    Returns:
        :obj:`StatsGraph <pyeitaa.raw.base.StatsGraph>`
    """

    __slots__: List[str] = ["token", "x"]

    ID = 0x621d5fa0
    QUALNAME = "functions.stats.LoadAsyncGraph"

    def __init__(self, *, token: str, x: Optional[int] = None) -> None:
        self.token = token  # string
        self.x = x  # flags.0?long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        token = String.read(data)
        
        x = Long.read(data) if flags & (1 << 0) else None
        return LoadAsyncGraph(token=token, x=x)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.x is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.token))
        
        if self.x is not None:
            data.write(Long(self.x))
        
        return data.getvalue()
