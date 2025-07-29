from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateDialogFiltersOrder(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x3a9c3e1c``

    Parameters:
        order: List of ``int`` ``32-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["order"]

    ID = -0x3a9c3e1c
    QUALNAME = "functions.messages.UpdateDialogFiltersOrder"

    def __init__(self, *, order: List[int]) -> None:
        self.order = order  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        order = TLObject.read(data, Int)
        
        return UpdateDialogFiltersOrder(order=order)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.order, Int))
        
        return data.getvalue()
