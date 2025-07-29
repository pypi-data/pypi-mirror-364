from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InvokeWithLayer(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x2564f2f3``

    Parameters:
        layer: ``int`` ``32-bit``
        query: Any method from :obj:`~pyeitaa.raw.functions`

    Returns:
        Any object from :obj:`~pyeitaa.raw.types`
    """

    __slots__: List[str] = ["layer", "query"]

    ID = -0x2564f2f3
    QUALNAME = "functions.InvokeWithLayer"

    def __init__(self, *, layer: int, query: TLObject) -> None:
        self.layer = layer  # int
        self.query = query  # !X

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        layer = Int.read(data)
        
        query = TLObject.read(data)
        
        return InvokeWithLayer(layer=layer, query=query)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.layer))
        
        data.write(self.query.write())
        
        return data.getvalue()
