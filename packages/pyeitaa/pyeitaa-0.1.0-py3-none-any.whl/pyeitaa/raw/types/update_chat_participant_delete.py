from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateChatParticipantDelete(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1cd0c289``

    Parameters:
        chat_id: ``int`` ``64-bit``
        user_id: ``int`` ``64-bit``
        version: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["chat_id", "user_id", "version"]

    ID = -0x1cd0c289
    QUALNAME = "types.UpdateChatParticipantDelete"

    def __init__(self, *, chat_id: int, user_id: int, version: int) -> None:
        self.chat_id = chat_id  # long
        self.user_id = user_id  # long
        self.version = version  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Long.read(data)
        
        user_id = Long.read(data)
        
        version = Int.read(data)
        
        return UpdateChatParticipantDelete(chat_id=chat_id, user_id=user_id, version=version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.chat_id))
        
        data.write(Long(self.user_id))
        
        data.write(Int(self.version))
        
        return data.getvalue()
