from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InvokeWithTakeout(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x535602d2``

    Parameters:
        takeout_id: ``int`` ``64-bit``
        query: Any method from :obj:`~pyeitaa.raw.functions`

    Returns:
        Any object from :obj:`~pyeitaa.raw.types`
    """

    __slots__: List[str] = ["takeout_id", "query"]

    ID = -0x535602d2
    QUALNAME = "functions.InvokeWithTakeout"

    def __init__(self, *, takeout_id: int, query: TLObject) -> None:
        self.takeout_id = takeout_id  # long
        self.query = query  # !X

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        takeout_id = Long.read(data)
        
        query = TLObject.read(data)
        
        return InvokeWithTakeout(takeout_id=takeout_id, query=query)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.takeout_id))
        
        data.write(self.query.write())
        
        return data.getvalue()
