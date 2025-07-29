from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AnswerWebhookJSONQuery(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x19dec0b3``

    Parameters:
        query_id: ``int`` ``64-bit``
        data: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["query_id", "data"]

    ID = -0x19dec0b3
    QUALNAME = "functions.bots.AnswerWebhookJSONQuery"

    def __init__(self, *, query_id: int, data: "raw.base.DataJSON") -> None:
        self.query_id = query_id  # long
        self.data = data  # DataJSON

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        query_id = Long.read(data)
        
        data = TLObject.read(data)
        
        return AnswerWebhookJSONQuery(query_id=query_id, data=data)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.query_id))
        
        data.write(self.data.write())
        
        return data.getvalue()
