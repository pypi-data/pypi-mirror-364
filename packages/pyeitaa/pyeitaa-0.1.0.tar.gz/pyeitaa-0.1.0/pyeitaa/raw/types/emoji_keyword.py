from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EmojiKeyword(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EmojiKeyword`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2a4c4607``

    Parameters:
        keyword: ``str``
        emoticons: List of ``str``
    """

    __slots__: List[str] = ["keyword", "emoticons"]

    ID = -0x2a4c4607
    QUALNAME = "types.EmojiKeyword"

    def __init__(self, *, keyword: str, emoticons: List[str]) -> None:
        self.keyword = keyword  # string
        self.emoticons = emoticons  # Vector<string>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        keyword = String.read(data)
        
        emoticons = TLObject.read(data, String)
        
        return EmojiKeyword(keyword=keyword, emoticons=emoticons)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.keyword))
        
        data.write(Vector(self.emoticons, String))
        
        return data.getvalue()
