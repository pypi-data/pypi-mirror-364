from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputPeerChat(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputPeer`.

    Details:
        - Layer: ``135``
        - ID: ``0x35a95cb9``

    Parameters:
        chat_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["chat_id"]

    ID = 0x35a95cb9
    QUALNAME = "types.InputPeerChat"

    def __init__(self, *, chat_id: int) -> None:
        self.chat_id = chat_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Long.read(data)
        
        return InputPeerChat(chat_id=chat_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.chat_id))
        
        return data.getvalue()
