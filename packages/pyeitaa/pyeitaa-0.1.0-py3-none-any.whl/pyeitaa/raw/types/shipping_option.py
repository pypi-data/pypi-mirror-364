from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ShippingOption(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ShippingOption`.

    Details:
        - Layer: ``135``
        - ID: ``-0x49dec321``

    Parameters:
        id: ``str``
        title: ``str``
        prices: List of :obj:`LabeledPrice <pyeitaa.raw.base.LabeledPrice>`
    """

    __slots__: List[str] = ["id", "title", "prices"]

    ID = -0x49dec321
    QUALNAME = "types.ShippingOption"

    def __init__(self, *, id: str, title: str, prices: List["raw.base.LabeledPrice"]) -> None:
        self.id = id  # string
        self.title = title  # string
        self.prices = prices  # Vector<LabeledPrice>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = String.read(data)
        
        title = String.read(data)
        
        prices = TLObject.read(data)
        
        return ShippingOption(id=id, title=title, prices=prices)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.id))
        
        data.write(String(self.title))
        
        data.write(Vector(self.prices))
        
        return data.getvalue()
