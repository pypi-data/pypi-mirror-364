from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EncryptedMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EncryptedMessage`.

    Details:
        - Layer: ``135``
        - ID: ``-0x12e73ee8``

    Parameters:
        random_id: ``int`` ``64-bit``
        chat_id: ``int`` ``32-bit``
        date: ``int`` ``32-bit``
        bytes: ``bytes``
        file: :obj:`EncryptedFile <pyeitaa.raw.base.EncryptedFile>`
    """

    __slots__: List[str] = ["random_id", "chat_id", "date", "bytes", "file"]

    ID = -0x12e73ee8
    QUALNAME = "types.EncryptedMessage"

    def __init__(self, *, random_id: int, chat_id: int, date: int, bytes: bytes, file: "raw.base.EncryptedFile") -> None:
        self.random_id = random_id  # long
        self.chat_id = chat_id  # int
        self.date = date  # int
        self.bytes = bytes  # bytes
        self.file = file  # EncryptedFile

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        random_id = Long.read(data)
        
        chat_id = Int.read(data)
        
        date = Int.read(data)
        
        bytes = Bytes.read(data)
        
        file = TLObject.read(data)
        
        return EncryptedMessage(random_id=random_id, chat_id=chat_id, date=date, bytes=bytes, file=file)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.random_id))
        
        data.write(Int(self.chat_id))
        
        data.write(Int(self.date))
        
        data.write(Bytes(self.bytes))
        
        data.write(self.file.write())
        
        return data.getvalue()
