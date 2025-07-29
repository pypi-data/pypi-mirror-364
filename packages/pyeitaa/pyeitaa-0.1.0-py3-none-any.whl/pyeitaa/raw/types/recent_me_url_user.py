from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class RecentMeUrlUser(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RecentMeUrl`.

    Details:
        - Layer: ``135``
        - ID: ``-0x46d3f61e``

    Parameters:
        url: ``str``
        user_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["url", "user_id"]

    ID = -0x46d3f61e
    QUALNAME = "types.RecentMeUrlUser"

    def __init__(self, *, url: str, user_id: int) -> None:
        self.url = url  # string
        self.user_id = user_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        url = String.read(data)
        
        user_id = Long.read(data)
        
        return RecentMeUrlUser(url=url, user_id=user_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.url))
        
        data.write(Long(self.user_id))
        
        return data.getvalue()
