from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class RecentMeUrlChat(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RecentMeUrl`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4d258e2e``

    Parameters:
        url: ``str``
        chat_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["url", "chat_id"]

    ID = -0x4d258e2e
    QUALNAME = "types.RecentMeUrlChat"

    def __init__(self, *, url: str, chat_id: int) -> None:
        self.url = url  # string
        self.chat_id = chat_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        url = String.read(data)
        
        chat_id = Long.read(data)
        
        return RecentMeUrlChat(url=url, chat_id=chat_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.url))
        
        data.write(Long(self.chat_id))
        
        return data.getvalue()
