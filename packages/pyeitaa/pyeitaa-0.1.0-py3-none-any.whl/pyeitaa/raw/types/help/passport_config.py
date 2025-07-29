from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PassportConfig(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.PassportConfig`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5f672951``

    Parameters:
        hash: ``int`` ``32-bit``
        countries_langs: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetPassportConfig <pyeitaa.raw.functions.help.GetPassportConfig>`
    """

    __slots__: List[str] = ["hash", "countries_langs"]

    ID = -0x5f672951
    QUALNAME = "types.help.PassportConfig"

    def __init__(self, *, hash: int, countries_langs: "raw.base.DataJSON") -> None:
        self.hash = hash  # int
        self.countries_langs = countries_langs  # DataJSON

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Int.read(data)
        
        countries_langs = TLObject.read(data)
        
        return PassportConfig(hash=hash, countries_langs=countries_langs)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.hash))
        
        data.write(self.countries_langs.write())
        
        return data.getvalue()
