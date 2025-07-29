from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PageBlockAnchor(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``-0x31f2c850``

    Parameters:
        name: ``str``
    """

    __slots__: List[str] = ["name"]

    ID = -0x31f2c850
    QUALNAME = "types.PageBlockAnchor"

    def __init__(self, *, name: str) -> None:
        self.name = name  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        name = String.read(data)
        
        return PageBlockAnchor(name=name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.name))
        
        return data.getvalue()
