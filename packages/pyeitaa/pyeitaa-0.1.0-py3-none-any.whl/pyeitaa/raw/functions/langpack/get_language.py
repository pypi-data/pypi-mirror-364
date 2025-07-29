from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetLanguage(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x6a596502``

    Parameters:
        lang_pack: ``str``
        lang_code: ``str``

    Returns:
        :obj:`LangPackLanguage <pyeitaa.raw.base.LangPackLanguage>`
    """

    __slots__: List[str] = ["lang_pack", "lang_code"]

    ID = 0x6a596502
    QUALNAME = "functions.langpack.GetLanguage"

    def __init__(self, *, lang_pack: str, lang_code: str) -> None:
        self.lang_pack = lang_pack  # string
        self.lang_code = lang_code  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        lang_pack = String.read(data)
        
        lang_code = String.read(data)
        
        return GetLanguage(lang_pack=lang_pack, lang_code=lang_code)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.lang_pack))
        
        data.write(String(self.lang_code))
        
        return data.getvalue()
