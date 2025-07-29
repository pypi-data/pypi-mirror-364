from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetDifference(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x3267b55b``

    Parameters:
        lang_pack: ``str``
        lang_code: ``str``
        from_version: ``int`` ``32-bit``

    Returns:
        :obj:`LangPackDifference <pyeitaa.raw.base.LangPackDifference>`
    """

    __slots__: List[str] = ["lang_pack", "lang_code", "from_version"]

    ID = -0x3267b55b
    QUALNAME = "functions.langpack.GetDifference"

    def __init__(self, *, lang_pack: str, lang_code: str, from_version: int) -> None:
        self.lang_pack = lang_pack  # string
        self.lang_code = lang_code  # string
        self.from_version = from_version  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        lang_pack = String.read(data)
        
        lang_code = String.read(data)
        
        from_version = Int.read(data)
        
        return GetDifference(lang_pack=lang_pack, lang_code=lang_code, from_version=from_version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.lang_pack))
        
        data.write(String(self.lang_code))
        
        data.write(Int(self.from_version))
        
        return data.getvalue()
