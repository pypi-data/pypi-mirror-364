from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateBotShippingQuery(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4a510283``

    Parameters:
        query_id: ``int`` ``64-bit``
        user_id: ``int`` ``64-bit``
        payload: ``bytes``
        shipping_address: :obj:`PostAddress <pyeitaa.raw.base.PostAddress>`
    """

    __slots__: List[str] = ["query_id", "user_id", "payload", "shipping_address"]

    ID = -0x4a510283
    QUALNAME = "types.UpdateBotShippingQuery"

    def __init__(self, *, query_id: int, user_id: int, payload: bytes, shipping_address: "raw.base.PostAddress") -> None:
        self.query_id = query_id  # long
        self.user_id = user_id  # long
        self.payload = payload  # bytes
        self.shipping_address = shipping_address  # PostAddress

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        query_id = Long.read(data)
        
        user_id = Long.read(data)
        
        payload = Bytes.read(data)
        
        shipping_address = TLObject.read(data)
        
        return UpdateBotShippingQuery(query_id=query_id, user_id=user_id, payload=payload, shipping_address=shipping_address)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.query_id))
        
        data.write(Long(self.user_id))
        
        data.write(Bytes(self.payload))
        
        data.write(self.shipping_address.write())
        
        return data.getvalue()
