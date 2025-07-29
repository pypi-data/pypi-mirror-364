from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class HttpWait(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x6d66ca61``

    Parameters:
        max_delay: ``int`` ``32-bit``
        wait_after: ``int`` ``32-bit``
        max_wait: ``int`` ``32-bit``

    Returns:
        :obj:`HttpWait <pyeitaa.raw.base.HttpWait>`
    """

    __slots__: List[str] = ["max_delay", "wait_after", "max_wait"]

    ID = -0x6d66ca61
    QUALNAME = "functions.HttpWait"

    def __init__(self, *, max_delay: int, wait_after: int, max_wait: int) -> None:
        self.max_delay = max_delay  # int
        self.wait_after = wait_after  # int
        self.max_wait = max_wait  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        max_delay = Int.read(data)
        
        wait_after = Int.read(data)
        
        max_wait = Int.read(data)
        
        return HttpWait(max_delay=max_delay, wait_after=wait_after, max_wait=max_wait)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.max_delay))
        
        data.write(Int(self.wait_after))
        
        data.write(Int(self.max_wait))
        
        return data.getvalue()
