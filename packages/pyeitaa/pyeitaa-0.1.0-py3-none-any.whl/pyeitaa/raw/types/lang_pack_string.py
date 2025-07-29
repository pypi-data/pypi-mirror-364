from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class LangPackString(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.LangPackString`.

    Details:
        - Layer: ``135``
        - ID: ``-0x352e7e0a``

    Parameters:
        key: ``str``
        value: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`langpack.GetStrings <pyeitaa.raw.functions.langpack.GetStrings>`
    """

    __slots__: List[str] = ["key", "value"]

    ID = -0x352e7e0a
    QUALNAME = "types.LangPackString"

    def __init__(self, *, key: str, value: str) -> None:
        self.key = key  # string
        self.value = value  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        key = String.read(data)
        
        value = String.read(data)
        
        return LangPackString(key=key, value=value)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.key))
        
        data.write(String(self.value))
        
        return data.getvalue()
