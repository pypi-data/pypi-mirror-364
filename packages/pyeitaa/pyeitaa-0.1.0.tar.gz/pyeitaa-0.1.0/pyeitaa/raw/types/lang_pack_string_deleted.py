from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class LangPackStringDeleted(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.LangPackString`.

    Details:
        - Layer: ``135``
        - ID: ``0x2979eeb2``

    Parameters:
        key: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`langpack.GetStrings <pyeitaa.raw.functions.langpack.GetStrings>`
    """

    __slots__: List[str] = ["key"]

    ID = 0x2979eeb2
    QUALNAME = "types.LangPackStringDeleted"

    def __init__(self, *, key: str) -> None:
        self.key = key  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        key = String.read(data)
        
        return LangPackStringDeleted(key=key)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.key))
        
        return data.getvalue()
