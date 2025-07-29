from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Double
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class JsonNumber(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.JSONValue`.

    Details:
        - Layer: ``135``
        - ID: ``0x2be0dfa4``

    Parameters:
        value: ``float`` ``64-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetAppConfig <pyeitaa.raw.functions.help.GetAppConfig>`
    """

    __slots__: List[str] = ["value"]

    ID = 0x2be0dfa4
    QUALNAME = "types.JsonNumber"

    def __init__(self, *, value: float) -> None:
        self.value = value  # double

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        value = Double.read(data)
        
        return JsonNumber(value=value)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Double(self.value))
        
        return data.getvalue()
