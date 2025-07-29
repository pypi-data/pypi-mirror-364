from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class CountriesList(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.CountriesList`.

    Details:
        - Layer: ``135``
        - ID: ``-0x782f8a62``

    Parameters:
        countries: List of :obj:`help.Country <pyeitaa.raw.base.help.Country>`
        hash: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetCountriesList <pyeitaa.raw.functions.help.GetCountriesList>`
    """

    __slots__: List[str] = ["countries", "hash"]

    ID = -0x782f8a62
    QUALNAME = "types.help.CountriesList"

    def __init__(self, *, countries: List["raw.base.help.Country"], hash: int) -> None:
        self.countries = countries  # Vector<help.Country>
        self.hash = hash  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        countries = TLObject.read(data)
        
        hash = Int.read(data)
        
        return CountriesList(countries=countries, hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.countries))
        
        data.write(Int(self.hash))
        
        return data.getvalue()
