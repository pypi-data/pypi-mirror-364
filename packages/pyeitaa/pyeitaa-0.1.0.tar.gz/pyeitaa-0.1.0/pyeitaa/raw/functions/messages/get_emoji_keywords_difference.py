from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetEmojiKeywordsDifference(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1508b6af``

    Parameters:
        lang_code: ``str``
        from_version: ``int`` ``32-bit``

    Returns:
        :obj:`EmojiKeywordsDifference <pyeitaa.raw.base.EmojiKeywordsDifference>`
    """

    __slots__: List[str] = ["lang_code", "from_version"]

    ID = 0x1508b6af
    QUALNAME = "functions.messages.GetEmojiKeywordsDifference"

    def __init__(self, *, lang_code: str, from_version: int) -> None:
        self.lang_code = lang_code  # string
        self.from_version = from_version  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        lang_code = String.read(data)
        
        from_version = Int.read(data)
        
        return GetEmojiKeywordsDifference(lang_code=lang_code, from_version=from_version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.lang_code))
        
        data.write(Int(self.from_version))
        
        return data.getvalue()
