from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PostAddress(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PostAddress`.

    Details:
        - Layer: ``135``
        - ID: ``0x1e8caaeb``

    Parameters:
        street_line1: ``str``
        street_line2: ``str``
        city: ``str``
        state: ``str``
        country_iso2: ``str``
        post_code: ``str``
    """

    __slots__: List[str] = ["street_line1", "street_line2", "city", "state", "country_iso2", "post_code"]

    ID = 0x1e8caaeb
    QUALNAME = "types.PostAddress"

    def __init__(self, *, street_line1: str, street_line2: str, city: str, state: str, country_iso2: str, post_code: str) -> None:
        self.street_line1 = street_line1  # string
        self.street_line2 = street_line2  # string
        self.city = city  # string
        self.state = state  # string
        self.country_iso2 = country_iso2  # string
        self.post_code = post_code  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        street_line1 = String.read(data)
        
        street_line2 = String.read(data)
        
        city = String.read(data)
        
        state = String.read(data)
        
        country_iso2 = String.read(data)
        
        post_code = String.read(data)
        
        return PostAddress(street_line1=street_line1, street_line2=street_line2, city=city, state=state, country_iso2=country_iso2, post_code=post_code)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.street_line1))
        
        data.write(String(self.street_line2))
        
        data.write(String(self.city))
        
        data.write(String(self.state))
        
        data.write(String(self.country_iso2))
        
        data.write(String(self.post_code))
        
        return data.getvalue()
