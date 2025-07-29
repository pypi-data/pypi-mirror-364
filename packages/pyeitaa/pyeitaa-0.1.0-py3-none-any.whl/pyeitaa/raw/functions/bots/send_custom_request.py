from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SendCustomRequest(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x55d89613``

    Parameters:
        custom_method: ``str``
        params: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`

    Returns:
        :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
    """

    __slots__: List[str] = ["custom_method", "params"]

    ID = -0x55d89613
    QUALNAME = "functions.bots.SendCustomRequest"

    def __init__(self, *, custom_method: str, params: "raw.base.DataJSON") -> None:
        self.custom_method = custom_method  # string
        self.params = params  # DataJSON

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        custom_method = String.read(data)
        
        params = TLObject.read(data)
        
        return SendCustomRequest(custom_method=custom_method, params=params)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.custom_method))
        
        data.write(self.params.write())
        
        return data.getvalue()
