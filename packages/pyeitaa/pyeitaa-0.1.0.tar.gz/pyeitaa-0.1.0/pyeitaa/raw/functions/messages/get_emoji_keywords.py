from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetEmojiKeywords(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x35a0e062``

    Parameters:
        lang_code: ``str``

    Returns:
        :obj:`EmojiKeywordsDifference <pyeitaa.raw.base.EmojiKeywordsDifference>`
    """

    __slots__: List[str] = ["lang_code"]

    ID = 0x35a0e062
    QUALNAME = "functions.messages.GetEmojiKeywords"

    def __init__(self, *, lang_code: str) -> None:
        self.lang_code = lang_code  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        lang_code = String.read(data)
        
        return GetEmojiKeywords(lang_code=lang_code)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.lang_code))
        
        return data.getvalue()
