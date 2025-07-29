from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputPaymentCredentials(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputPaymentCredentials`.

    Details:
        - Layer: ``135``
        - ID: ``0x3417d728``

    Parameters:
        data: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
        save (optional): ``bool``
    """

    __slots__: List[str] = ["data", "save"]

    ID = 0x3417d728
    QUALNAME = "types.InputPaymentCredentials"

    def __init__(self, *, data: "raw.base.DataJSON", save: Optional[bool] = None) -> None:
        self.data = data  # DataJSON
        self.save = save  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        save = True if flags & (1 << 0) else False
        data = TLObject.read(data)
        
        return InputPaymentCredentials(data=data, save=save)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.save else 0
        data.write(Int(flags))
        
        data.write(self.data.write())
        
        return data.getvalue()
