from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class LangPackDifference(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.LangPackDifference`.

    Details:
        - Layer: ``135``
        - ID: ``-0xc7a3e0a``

    Parameters:
        lang_code: ``str``
        from_version: ``int`` ``32-bit``
        version: ``int`` ``32-bit``
        strings: List of :obj:`LangPackString <pyeitaa.raw.base.LangPackString>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`langpack.GetLangPack <pyeitaa.raw.functions.langpack.GetLangPack>`
            - :obj:`langpack.GetDifference <pyeitaa.raw.functions.langpack.GetDifference>`
    """

    __slots__: List[str] = ["lang_code", "from_version", "version", "strings"]

    ID = -0xc7a3e0a
    QUALNAME = "types.LangPackDifference"

    def __init__(self, *, lang_code: str, from_version: int, version: int, strings: List["raw.base.LangPackString"]) -> None:
        self.lang_code = lang_code  # string
        self.from_version = from_version  # int
        self.version = version  # int
        self.strings = strings  # Vector<LangPackString>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        lang_code = String.read(data)
        
        from_version = Int.read(data)
        
        version = Int.read(data)
        
        strings = TLObject.read(data)
        
        return LangPackDifference(lang_code=lang_code, from_version=from_version, version=version, strings=strings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.lang_code))
        
        data.write(Int(self.from_version))
        
        data.write(Int(self.version))
        
        data.write(Vector(self.strings))
        
        return data.getvalue()
