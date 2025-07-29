from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateDialogFilterOrder(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5a28defb``

    Parameters:
        order: List of ``int`` ``32-bit``
    """

    __slots__: List[str] = ["order"]

    ID = -0x5a28defb
    QUALNAME = "types.UpdateDialogFilterOrder"

    def __init__(self, *, order: List[int]) -> None:
        self.order = order  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        order = TLObject.read(data, Int)
        
        return UpdateDialogFilterOrder(order=order)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.order, Int))
        
        return data.getvalue()
