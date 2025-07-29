from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetEmojiKeywordsLanguages(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x4e9963b2``

    Parameters:
        lang_codes: List of ``str``

    Returns:
        List of :obj:`EmojiLanguage <pyeitaa.raw.base.EmojiLanguage>`
    """

    __slots__: List[str] = ["lang_codes"]

    ID = 0x4e9963b2
    QUALNAME = "functions.messages.GetEmojiKeywordsLanguages"

    def __init__(self, *, lang_codes: List[str]) -> None:
        self.lang_codes = lang_codes  # Vector<string>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        lang_codes = TLObject.read(data, String)
        
        return GetEmojiKeywordsLanguages(lang_codes=lang_codes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.lang_codes, String))
        
        return data.getvalue()
