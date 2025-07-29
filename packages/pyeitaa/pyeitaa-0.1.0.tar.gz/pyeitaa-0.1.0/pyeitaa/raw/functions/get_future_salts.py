from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetFutureSalts(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x46de42fc``

    Parameters:
        num: ``int`` ``32-bit``

    Returns:
        :obj:`FutureSalts <pyeitaa.raw.base.FutureSalts>`
    """

    __slots__: List[str] = ["num"]

    ID = -0x46de42fc
    QUALNAME = "functions.GetFutureSalts"

    def __init__(self, *, num: int) -> None:
        self.num = num  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        num = Int.read(data)
        
        return GetFutureSalts(num=num)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.num))
        
        return data.getvalue()
