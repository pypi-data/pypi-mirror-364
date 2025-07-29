from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateDcOptions(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x71a1678d``

    Parameters:
        dc_options: List of :obj:`DcOption <pyeitaa.raw.base.DcOption>`
    """

    __slots__: List[str] = ["dc_options"]

    ID = -0x71a1678d
    QUALNAME = "types.UpdateDcOptions"

    def __init__(self, *, dc_options: List["raw.base.DcOption"]) -> None:
        self.dc_options = dc_options  # Vector<DcOption>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        dc_options = TLObject.read(data)
        
        return UpdateDcOptions(dc_options=dc_options)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.dc_options))
        
        return data.getvalue()
