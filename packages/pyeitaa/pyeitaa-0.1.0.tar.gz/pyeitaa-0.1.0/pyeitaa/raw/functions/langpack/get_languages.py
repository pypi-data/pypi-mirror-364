from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetLanguages(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x42c6978f``

    Parameters:
        lang_pack: ``str``

    Returns:
        List of :obj:`LangPackLanguage <pyeitaa.raw.base.LangPackLanguage>`
    """

    __slots__: List[str] = ["lang_pack"]

    ID = 0x42c6978f
    QUALNAME = "functions.langpack.GetLanguages"

    def __init__(self, *, lang_pack: str) -> None:
        self.lang_pack = lang_pack  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        lang_pack = String.read(data)
        
        return GetLanguages(lang_pack=lang_pack)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.lang_pack))
        
        return data.getvalue()
