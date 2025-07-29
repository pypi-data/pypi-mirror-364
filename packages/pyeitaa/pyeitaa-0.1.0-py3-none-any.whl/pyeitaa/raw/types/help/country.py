from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class Country(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.Country`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3c7871dd``

    Parameters:
        iso2: ``str``
        default_name: ``str``
        country_codes: List of :obj:`help.CountryCode <pyeitaa.raw.base.help.CountryCode>`
        hidden (optional): ``bool``
        name (optional): ``str``
    """

    __slots__: List[str] = ["iso2", "default_name", "country_codes", "hidden", "name"]

    ID = -0x3c7871dd
    QUALNAME = "types.help.Country"

    def __init__(self, *, iso2: str, default_name: str, country_codes: List["raw.base.help.CountryCode"], hidden: Optional[bool] = None, name: Optional[str] = None) -> None:
        self.iso2 = iso2  # string
        self.default_name = default_name  # string
        self.country_codes = country_codes  # Vector<help.CountryCode>
        self.hidden = hidden  # flags.0?true
        self.name = name  # flags.1?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        hidden = True if flags & (1 << 0) else False
        iso2 = String.read(data)
        
        default_name = String.read(data)
        
        name = String.read(data) if flags & (1 << 1) else None
        country_codes = TLObject.read(data)
        
        return Country(iso2=iso2, default_name=default_name, country_codes=country_codes, hidden=hidden, name=name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.hidden else 0
        flags |= (1 << 1) if self.name is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.iso2))
        
        data.write(String(self.default_name))
        
        if self.name is not None:
            data.write(String(self.name))
        
        data.write(Vector(self.country_codes))
        
        return data.getvalue()
