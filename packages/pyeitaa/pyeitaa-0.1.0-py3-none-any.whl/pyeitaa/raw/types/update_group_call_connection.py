from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdateGroupCallConnection(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0xb783982``

    Parameters:
        params: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
        presentation (optional): ``bool``
    """

    __slots__: List[str] = ["params", "presentation"]

    ID = 0xb783982
    QUALNAME = "types.UpdateGroupCallConnection"

    def __init__(self, *, params: "raw.base.DataJSON", presentation: Optional[bool] = None) -> None:
        self.params = params  # DataJSON
        self.presentation = presentation  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        presentation = True if flags & (1 << 0) else False
        params = TLObject.read(data)
        
        return UpdateGroupCallConnection(params=params, presentation=presentation)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.presentation else 0
        data.write(Int(flags))
        
        data.write(self.params.write())
        
        return data.getvalue()
