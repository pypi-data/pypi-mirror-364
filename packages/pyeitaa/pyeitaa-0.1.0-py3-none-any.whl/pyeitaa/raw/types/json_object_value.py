from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class JsonObjectValue(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.JSONObjectValue`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3f21e427``

    Parameters:
        key: ``str``
        value: :obj:`JSONValue <pyeitaa.raw.base.JSONValue>`
    """

    __slots__: List[str] = ["key", "value"]

    ID = -0x3f21e427
    QUALNAME = "types.JsonObjectValue"

    def __init__(self, *, key: str, value: "raw.base.JSONValue") -> None:
        self.key = key  # string
        self.value = value  # JSONValue

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        key = String.read(data)
        
        value = TLObject.read(data)
        
        return JsonObjectValue(key=key, value=value)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.key))
        
        data.write(self.value.write())
        
        return data.getvalue()
