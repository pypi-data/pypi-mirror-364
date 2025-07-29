from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SupportName(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.SupportName`.

    Details:
        - Layer: ``135``
        - ID: ``-0x73fa0e37``

    Parameters:
        name: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetSupportName <pyeitaa.raw.functions.help.GetSupportName>`
    """

    __slots__: List[str] = ["name"]

    ID = -0x73fa0e37
    QUALNAME = "types.help.SupportName"

    def __init__(self, *, name: str) -> None:
        self.name = name  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        name = String.read(data)
        
        return SupportName(name=name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.name))
        
        return data.getvalue()
