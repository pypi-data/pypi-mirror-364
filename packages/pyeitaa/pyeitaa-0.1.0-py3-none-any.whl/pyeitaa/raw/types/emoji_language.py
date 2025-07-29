from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EmojiLanguage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EmojiLanguage`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4c04ac9f``

    Parameters:
        lang_code: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetEmojiKeywordsLanguages <pyeitaa.raw.functions.messages.GetEmojiKeywordsLanguages>`
    """

    __slots__: List[str] = ["lang_code"]

    ID = -0x4c04ac9f
    QUALNAME = "types.EmojiLanguage"

    def __init__(self, *, lang_code: str) -> None:
        self.lang_code = lang_code  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        lang_code = String.read(data)
        
        return EmojiLanguage(lang_code=lang_code)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.lang_code))
        
        return data.getvalue()
