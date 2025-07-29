from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputEncryptedChat(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputEncryptedChat`.

    Details:
        - Layer: ``135``
        - ID: ``-0xebe4a1f``

    Parameters:
        chat_id: ``int`` ``32-bit``
        access_hash: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["chat_id", "access_hash"]

    ID = -0xebe4a1f
    QUALNAME = "types.InputEncryptedChat"

    def __init__(self, *, chat_id: int, access_hash: int) -> None:
        self.chat_id = chat_id  # int
        self.access_hash = access_hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Int.read(data)
        
        access_hash = Long.read(data)
        
        return InputEncryptedChat(chat_id=chat_id, access_hash=access_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.chat_id))
        
        data.write(Long(self.access_hash))
        
        return data.getvalue()
