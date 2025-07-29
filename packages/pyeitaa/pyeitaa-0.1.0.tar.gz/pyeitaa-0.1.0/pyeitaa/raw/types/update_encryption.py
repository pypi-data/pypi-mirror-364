from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateEncryption(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4b5d1773``

    Parameters:
        chat: :obj:`EncryptedChat <pyeitaa.raw.base.EncryptedChat>`
        date: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["chat", "date"]

    ID = -0x4b5d1773
    QUALNAME = "types.UpdateEncryption"

    def __init__(self, *, chat: "raw.base.EncryptedChat", date: int) -> None:
        self.chat = chat  # EncryptedChat
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat = TLObject.read(data)
        
        date = Int.read(data)
        
        return UpdateEncryption(chat=chat, date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.chat.write())
        
        data.write(Int(self.date))
        
        return data.getvalue()
