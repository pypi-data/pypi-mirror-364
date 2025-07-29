from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class ChannelDifferenceEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.updates.ChannelDifference`.

    Details:
        - Layer: ``135``
        - ID: ``0x3e11affb``

    Parameters:
        pts: ``int`` ``32-bit``
        final (optional): ``bool``
        timeout (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`updates.GetChannelDifference <pyeitaa.raw.functions.updates.GetChannelDifference>`
    """

    __slots__: List[str] = ["pts", "final", "timeout"]

    ID = 0x3e11affb
    QUALNAME = "types.updates.ChannelDifferenceEmpty"

    def __init__(self, *, pts: int, final: Optional[bool] = None, timeout: Optional[int] = None) -> None:
        self.pts = pts  # int
        self.final = final  # flags.0?true
        self.timeout = timeout  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        final = True if flags & (1 << 0) else False
        pts = Int.read(data)
        
        timeout = Int.read(data) if flags & (1 << 1) else None
        return ChannelDifferenceEmpty(pts=pts, final=final, timeout=timeout)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.final else 0
        flags |= (1 << 1) if self.timeout is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.pts))
        
        if self.timeout is not None:
            data.write(Int(self.timeout))
        
        return data.getvalue()
