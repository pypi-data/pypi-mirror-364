from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetStrings(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x1015c7fd``

    Parameters:
        lang_pack: ``str``
        lang_code: ``str``
        keys: List of ``str``

    Returns:
        List of :obj:`LangPackString <pyeitaa.raw.base.LangPackString>`
    """

    __slots__: List[str] = ["lang_pack", "lang_code", "keys"]

    ID = -0x1015c7fd
    QUALNAME = "functions.langpack.GetStrings"

    def __init__(self, *, lang_pack: str, lang_code: str, keys: List[str]) -> None:
        self.lang_pack = lang_pack  # string
        self.lang_code = lang_code  # string
        self.keys = keys  # Vector<string>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        lang_pack = String.read(data)
        
        lang_code = String.read(data)
        
        keys = TLObject.read(data, String)
        
        return GetStrings(lang_pack=lang_pack, lang_code=lang_code, keys=keys)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.lang_pack))
        
        data.write(String(self.lang_code))
        
        data.write(Vector(self.keys, String))
        
        return data.getvalue()
