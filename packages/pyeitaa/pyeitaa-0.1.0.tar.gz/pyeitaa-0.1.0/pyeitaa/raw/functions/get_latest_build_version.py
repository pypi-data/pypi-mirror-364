from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetLatestBuildVersion(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0xfe439fa``

    Parameters:
        flags: ``int`` ``32-bit``

    Returns:
        :obj:`LatestBuildVersion <pyeitaa.raw.base.LatestBuildVersion>`
    """

    __slots__: List[str] = ["flags"]

    ID = 0xfe439fa
    QUALNAME = "functions.GetLatestBuildVersion"

    def __init__(self, *, flags: int) -> None:
        self.flags = flags  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        flags = Int.read(data)
        
        return GetLatestBuildVersion(flags=flags)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.flags))
        
        return data.getvalue()
