from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SetBotShippingResults(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x1a098d06``

    Parameters:
        query_id: ``int`` ``64-bit``
        error (optional): ``str``
        shipping_options (optional): List of :obj:`ShippingOption <pyeitaa.raw.base.ShippingOption>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["query_id", "error", "shipping_options"]

    ID = -0x1a098d06
    QUALNAME = "functions.messages.SetBotShippingResults"

    def __init__(self, *, query_id: int, error: Optional[str] = None, shipping_options: Optional[List["raw.base.ShippingOption"]] = None) -> None:
        self.query_id = query_id  # long
        self.error = error  # flags.0?string
        self.shipping_options = shipping_options  # flags.1?Vector<ShippingOption>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        query_id = Long.read(data)
        
        error = String.read(data) if flags & (1 << 0) else None
        shipping_options = TLObject.read(data) if flags & (1 << 1) else []
        
        return SetBotShippingResults(query_id=query_id, error=error, shipping_options=shipping_options)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.error is not None else 0
        flags |= (1 << 1) if self.shipping_options is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.query_id))
        
        if self.error is not None:
            data.write(String(self.error))
        
        if self.shipping_options is not None:
            data.write(Vector(self.shipping_options))
        
        return data.getvalue()
