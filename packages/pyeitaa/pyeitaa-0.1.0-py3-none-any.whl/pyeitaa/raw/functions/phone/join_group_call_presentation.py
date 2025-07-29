from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class JoinGroupCallPresentation(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x3415943c``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        params: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["call", "params"]

    ID = -0x3415943c
    QUALNAME = "functions.phone.JoinGroupCallPresentation"

    def __init__(self, *, call: "raw.base.InputGroupCall", params: "raw.base.DataJSON") -> None:
        self.call = call  # InputGroupCall
        self.params = params  # DataJSON

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        call = TLObject.read(data)
        
        params = TLObject.read(data)
        
        return JoinGroupCallPresentation(call=call, params=params)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.call.write())
        
        data.write(self.params.write())
        
        return data.getvalue()
