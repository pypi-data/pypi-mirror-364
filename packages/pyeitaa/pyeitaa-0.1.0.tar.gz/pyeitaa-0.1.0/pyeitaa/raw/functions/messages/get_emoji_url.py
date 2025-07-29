from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetEmojiURL(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x2a4ef3da``

    Parameters:
        lang_code: ``str``

    Returns:
        :obj:`EmojiURL <pyeitaa.raw.base.EmojiURL>`
    """

    __slots__: List[str] = ["lang_code"]

    ID = -0x2a4ef3da
    QUALNAME = "functions.messages.GetEmojiURL"

    def __init__(self, *, lang_code: str) -> None:
        self.lang_code = lang_code  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        lang_code = String.read(data)
        
        return GetEmojiURL(lang_code=lang_code)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.lang_code))
        
        return data.getvalue()
