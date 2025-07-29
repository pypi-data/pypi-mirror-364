from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class RecentMeUrlUnknown(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RecentMeUrl`.

    Details:
        - Layer: ``135``
        - ID: ``0x46e1d13d``

    Parameters:
        url: ``str``
    """

    __slots__: List[str] = ["url"]

    ID = 0x46e1d13d
    QUALNAME = "types.RecentMeUrlUnknown"

    def __init__(self, *, url: str) -> None:
        self.url = url  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        url = String.read(data)
        
        return RecentMeUrlUnknown(url=url)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.url))
        
        return data.getvalue()
