from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InvokeAfterMsg(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x3460c8d3``

    Parameters:
        msg_id: ``int`` ``64-bit``
        query: Any method from :obj:`~pyeitaa.raw.functions`

    Returns:
        Any object from :obj:`~pyeitaa.raw.types`
    """

    __slots__: List[str] = ["msg_id", "query"]

    ID = -0x3460c8d3
    QUALNAME = "functions.InvokeAfterMsg"

    def __init__(self, *, msg_id: int, query: TLObject) -> None:
        self.msg_id = msg_id  # long
        self.query = query  # !X

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        msg_id = Long.read(data)
        
        query = TLObject.read(data)
        
        return InvokeAfterMsg(msg_id=msg_id, query=query)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.msg_id))
        
        data.write(self.query.write())
        
        return data.getvalue()
