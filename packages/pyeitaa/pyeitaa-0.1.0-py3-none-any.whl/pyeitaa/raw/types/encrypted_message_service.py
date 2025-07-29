from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EncryptedMessageService(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EncryptedMessage`.

    Details:
        - Layer: ``135``
        - ID: ``0x23734b06``

    Parameters:
        random_id: ``int`` ``64-bit``
        chat_id: ``int`` ``32-bit``
        date: ``int`` ``32-bit``
        bytes: ``bytes``
    """

    __slots__: List[str] = ["random_id", "chat_id", "date", "bytes"]

    ID = 0x23734b06
    QUALNAME = "types.EncryptedMessageService"

    def __init__(self, *, random_id: int, chat_id: int, date: int, bytes: bytes) -> None:
        self.random_id = random_id  # long
        self.chat_id = chat_id  # int
        self.date = date  # int
        self.bytes = bytes  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        random_id = Long.read(data)
        
        chat_id = Int.read(data)
        
        date = Int.read(data)
        
        bytes = Bytes.read(data)
        
        return EncryptedMessageService(random_id=random_id, chat_id=chat_id, date=date, bytes=bytes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.random_id))
        
        data.write(Int(self.chat_id))
        
        data.write(Int(self.date))
        
        data.write(Bytes(self.bytes))
        
        return data.getvalue()
