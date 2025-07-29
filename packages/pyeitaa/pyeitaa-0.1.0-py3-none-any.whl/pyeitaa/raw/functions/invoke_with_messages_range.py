from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InvokeWithMessagesRange(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x365275f2``

    Parameters:
        range: :obj:`MessageRange <pyeitaa.raw.base.MessageRange>`
        query: Any method from :obj:`~pyeitaa.raw.functions`

    Returns:
        Any object from :obj:`~pyeitaa.raw.types`
    """

    __slots__: List[str] = ["range", "query"]

    ID = 0x365275f2
    QUALNAME = "functions.InvokeWithMessagesRange"

    def __init__(self, *, range: "raw.base.MessageRange", query: TLObject) -> None:
        self.range = range  # MessageRange
        self.query = query  # !X

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        range = TLObject.read(data)
        
        query = TLObject.read(data)
        
        return InvokeWithMessagesRange(range=range, query=query)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.range.write())
        
        data.write(self.query.write())
        
        return data.getvalue()
