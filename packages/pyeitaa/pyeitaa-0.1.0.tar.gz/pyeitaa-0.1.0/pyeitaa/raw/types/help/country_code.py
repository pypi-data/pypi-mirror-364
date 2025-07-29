from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class CountryCode(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.CountryCode`.

    Details:
        - Layer: ``135``
        - ID: ``0x4203c5ef``

    Parameters:
        country_code: ``str``
        prefixes (optional): List of ``str``
        patterns (optional): List of ``str``
    """

    __slots__: List[str] = ["country_code", "prefixes", "patterns"]

    ID = 0x4203c5ef
    QUALNAME = "types.help.CountryCode"

    def __init__(self, *, country_code: str, prefixes: Optional[List[str]] = None, patterns: Optional[List[str]] = None) -> None:
        self.country_code = country_code  # string
        self.prefixes = prefixes  # flags.0?Vector<string>
        self.patterns = patterns  # flags.1?Vector<string>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        country_code = String.read(data)
        
        prefixes = TLObject.read(data, String) if flags & (1 << 0) else []
        
        patterns = TLObject.read(data, String) if flags & (1 << 1) else []
        
        return CountryCode(country_code=country_code, prefixes=prefixes, patterns=patterns)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.prefixes is not None else 0
        flags |= (1 << 1) if self.patterns is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.country_code))
        
        if self.prefixes is not None:
            data.write(Vector(self.prefixes, String))
        
        if self.patterns is not None:
            data.write(Vector(self.patterns, String))
        
        return data.getvalue()
