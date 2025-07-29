from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateEncryptedMessagesRead(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x38fe25b7``

    Parameters:
        chat_id: ``int`` ``32-bit``
        max_date: ``int`` ``32-bit``
        date: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["chat_id", "max_date", "date"]

    ID = 0x38fe25b7
    QUALNAME = "types.UpdateEncryptedMessagesRead"

    def __init__(self, *, chat_id: int, max_date: int, date: int) -> None:
        self.chat_id = chat_id  # int
        self.max_date = max_date  # int
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Int.read(data)
        
        max_date = Int.read(data)
        
        date = Int.read(data)
        
        return UpdateEncryptedMessagesRead(chat_id=chat_id, max_date=max_date, date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.chat_id))
        
        data.write(Int(self.max_date))
        
        data.write(Int(self.date))
        
        return data.getvalue()
