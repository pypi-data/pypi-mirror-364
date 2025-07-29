from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class LabeledPrice(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.LabeledPrice`.

    Details:
        - Layer: ``135``
        - ID: ``-0x34d69408``

    Parameters:
        label: ``str``
        amount: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["label", "amount"]

    ID = -0x34d69408
    QUALNAME = "types.LabeledPrice"

    def __init__(self, *, label: str, amount: int) -> None:
        self.label = label  # string
        self.amount = amount  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        label = String.read(data)
        
        amount = Long.read(data)
        
        return LabeledPrice(label=label, amount=amount)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.label))
        
        data.write(Long(self.amount))
        
        return data.getvalue()
