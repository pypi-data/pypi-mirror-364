from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InvokeWithoutUpdates(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x406ba649``

    Parameters:
        query: Any method from :obj:`~pyeitaa.raw.functions`

    Returns:
        Any object from :obj:`~pyeitaa.raw.types`
    """

    __slots__: List[str] = ["query"]

    ID = -0x406ba649
    QUALNAME = "functions.InvokeWithoutUpdates"

    def __init__(self, *, query: TLObject) -> None:
        self.query = query  # !X

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        query = TLObject.read(data)
        
        return InvokeWithoutUpdates(query=query)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.query.write())
        
        return data.getvalue()
