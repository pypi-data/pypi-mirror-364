from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InvokeAfterMsgs(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3dc4b4f0``

    Parameters:
        msg_ids: List of ``int`` ``64-bit``
        query: Any method from :obj:`~pyeitaa.raw.functions`

    Returns:
        Any object from :obj:`~pyeitaa.raw.types`
    """

    __slots__: List[str] = ["msg_ids", "query"]

    ID = 0x3dc4b4f0
    QUALNAME = "functions.InvokeAfterMsgs"

    def __init__(self, *, msg_ids: List[int], query: TLObject) -> None:
        self.msg_ids = msg_ids  # Vector<long>
        self.query = query  # !X

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        msg_ids = TLObject.read(data, Long)
        
        query = TLObject.read(data)
        
        return InvokeAfterMsgs(msg_ids=msg_ids, query=query)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.msg_ids, Long))
        
        data.write(self.query.write())
        
        return data.getvalue()
