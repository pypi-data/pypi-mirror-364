from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class JsonBool(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.JSONValue`.

    Details:
        - Layer: ``135``
        - ID: ``-0x38cba196``

    Parameters:
        value: ``bool``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetAppConfig <pyeitaa.raw.functions.help.GetAppConfig>`
    """

    __slots__: List[str] = ["value"]

    ID = -0x38cba196
    QUALNAME = "types.JsonBool"

    def __init__(self, *, value: bool) -> None:
        self.value = value  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        value = Bool.read(data)
        
        return JsonBool(value=value)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bool(self.value))
        
        return data.getvalue()
