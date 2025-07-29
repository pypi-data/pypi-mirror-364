from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageActionChatEditPhoto(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x7fcb13a8``

    Parameters:
        photo: :obj:`Photo <pyeitaa.raw.base.Photo>`
    """

    __slots__: List[str] = ["photo"]

    ID = 0x7fcb13a8
    QUALNAME = "types.MessageActionChatEditPhoto"

    def __init__(self, *, photo: "raw.base.Photo") -> None:
        self.photo = photo  # Photo

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        photo = TLObject.read(data)
        
        return MessageActionChatEditPhoto(photo=photo)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.photo.write())
        
        return data.getvalue()
