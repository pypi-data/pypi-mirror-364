from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetCountriesList(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x735787a8``

    Parameters:
        lang_code: ``str``
        hash: ``int`` ``32-bit``

    Returns:
        :obj:`help.CountriesList <pyeitaa.raw.base.help.CountriesList>`
    """

    __slots__: List[str] = ["lang_code", "hash"]

    ID = 0x735787a8
    QUALNAME = "functions.help.GetCountriesList"

    def __init__(self, *, lang_code: str, hash: int) -> None:
        self.lang_code = lang_code  # string
        self.hash = hash  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        lang_code = String.read(data)
        
        hash = Int.read(data)
        
        return GetCountriesList(lang_code=lang_code, hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.lang_code))
        
        data.write(Int(self.hash))
        
        return data.getvalue()
