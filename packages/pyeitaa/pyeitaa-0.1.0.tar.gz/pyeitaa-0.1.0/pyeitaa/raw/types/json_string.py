from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class JsonString(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.JSONValue`.

    Details:
        - Layer: ``135``
        - ID: ``-0x48e18986``

    Parameters:
        value: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetAppConfig <pyeitaa.raw.functions.help.GetAppConfig>`
    """

    __slots__: List[str] = ["value"]

    ID = -0x48e18986
    QUALNAME = "types.JsonString"

    def __init__(self, *, value: str) -> None:
        self.value = value  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        value = String.read(data)
        
        return JsonString(value=value)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.value))
        
        return data.getvalue()
