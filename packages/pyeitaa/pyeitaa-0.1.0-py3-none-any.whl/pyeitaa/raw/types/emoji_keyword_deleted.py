from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EmojiKeywordDeleted(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EmojiKeyword`.

    Details:
        - Layer: ``135``
        - ID: ``0x236df622``

    Parameters:
        keyword: ``str``
        emoticons: List of ``str``
    """

    __slots__: List[str] = ["keyword", "emoticons"]

    ID = 0x236df622
    QUALNAME = "types.EmojiKeywordDeleted"

    def __init__(self, *, keyword: str, emoticons: List[str]) -> None:
        self.keyword = keyword  # string
        self.emoticons = emoticons  # Vector<string>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        keyword = String.read(data)
        
        emoticons = TLObject.read(data, String)
        
        return EmojiKeywordDeleted(keyword=keyword, emoticons=emoticons)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.keyword))
        
        data.write(Vector(self.emoticons, String))
        
        return data.getvalue()
