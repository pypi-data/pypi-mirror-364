from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EditChatPhoto(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x35ddd674``

    Parameters:
        chat_id: ``int`` ``64-bit``
        photo: :obj:`InputChatPhoto <pyeitaa.raw.base.InputChatPhoto>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["chat_id", "photo"]

    ID = 0x35ddd674
    QUALNAME = "functions.messages.EditChatPhoto"

    def __init__(self, *, chat_id: int, photo: "raw.base.InputChatPhoto") -> None:
        self.chat_id = chat_id  # long
        self.photo = photo  # InputChatPhoto

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Long.read(data)
        
        photo = TLObject.read(data)
        
        return EditChatPhoto(chat_id=chat_id, photo=photo)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.chat_id))
        
        data.write(self.photo.write())
        
        return data.getvalue()
