from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateBotWebhookJSONQuery(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x646dbf5a``

    Parameters:
        query_id: ``int`` ``64-bit``
        data: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
        timeout: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["query_id", "data", "timeout"]

    ID = -0x646dbf5a
    QUALNAME = "types.UpdateBotWebhookJSONQuery"

    def __init__(self, *, query_id: int, data: "raw.base.DataJSON", timeout: int) -> None:
        self.query_id = query_id  # long
        self.data = data  # DataJSON
        self.timeout = timeout  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        query_id = Long.read(data)
        
        data = TLObject.read(data)
        
        timeout = Int.read(data)
        
        return UpdateBotWebhookJSONQuery(query_id=query_id, data=data, timeout=timeout)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.query_id))
        
        data.write(self.data.write())
        
        data.write(Int(self.timeout))
        
        return data.getvalue()
