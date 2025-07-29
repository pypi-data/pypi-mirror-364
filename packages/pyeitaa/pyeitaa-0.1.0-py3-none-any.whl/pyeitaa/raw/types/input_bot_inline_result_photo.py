from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputBotInlineResultPhoto(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputBotInlineResult`.

    Details:
        - Layer: ``135``
        - ID: ``-0x57279b59``

    Parameters:
        id: ``str``
        type: ``str``
        photo: :obj:`InputPhoto <pyeitaa.raw.base.InputPhoto>`
        send_message: :obj:`InputBotInlineMessage <pyeitaa.raw.base.InputBotInlineMessage>`
    """

    __slots__: List[str] = ["id", "type", "photo", "send_message"]

    ID = -0x57279b59
    QUALNAME = "types.InputBotInlineResultPhoto"

    def __init__(self, *, id: str, type: str, photo: "raw.base.InputPhoto", send_message: "raw.base.InputBotInlineMessage") -> None:
        self.id = id  # string
        self.type = type  # string
        self.photo = photo  # InputPhoto
        self.send_message = send_message  # InputBotInlineMessage

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = String.read(data)
        
        type = String.read(data)
        
        photo = TLObject.read(data)
        
        send_message = TLObject.read(data)
        
        return InputBotInlineResultPhoto(id=id, type=type, photo=photo, send_message=send_message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.id))
        
        data.write(String(self.type))
        
        data.write(self.photo.write())
        
        data.write(self.send_message.write())
        
        return data.getvalue()
