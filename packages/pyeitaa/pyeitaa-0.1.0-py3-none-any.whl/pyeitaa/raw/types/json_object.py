from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class JsonObject(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.JSONValue`.

    Details:
        - Layer: ``135``
        - ID: ``-0x663e2b63``

    Parameters:
        value: List of :obj:`JSONObjectValue <pyeitaa.raw.base.JSONObjectValue>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetAppConfig <pyeitaa.raw.functions.help.GetAppConfig>`
    """

    __slots__: List[str] = ["value"]

    ID = -0x663e2b63
    QUALNAME = "types.JsonObject"

    def __init__(self, *, value: List["raw.base.JSONObjectValue"]) -> None:
        self.value = value  # Vector<JSONObjectValue>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        value = TLObject.read(data)
        
        return JsonObject(value=value)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.value))
        
        return data.getvalue()
