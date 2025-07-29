from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageMediaDice(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0x3f7ee58b``

    Parameters:
        value: ``int`` ``32-bit``
        emoticon: ``str``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyeitaa.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyeitaa.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyeitaa.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["value", "emoticon"]

    ID = 0x3f7ee58b
    QUALNAME = "types.MessageMediaDice"

    def __init__(self, *, value: int, emoticon: str) -> None:
        self.value = value  # int
        self.emoticon = emoticon  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        value = Int.read(data)
        
        emoticon = String.read(data)
        
        return MessageMediaDice(value=value, emoticon=emoticon)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.value))
        
        data.write(String(self.emoticon))
        
        return data.getvalue()
