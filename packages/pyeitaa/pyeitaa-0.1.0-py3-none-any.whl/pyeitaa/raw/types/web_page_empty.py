from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class WebPageEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.WebPage`.

    Details:
        - Layer: ``135``
        - ID: ``-0x14eb8818``

    Parameters:
        id: ``int`` ``64-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPage <pyeitaa.raw.functions.messages.GetWebPage>`
    """

    __slots__: List[str] = ["id"]

    ID = -0x14eb8818
    QUALNAME = "types.WebPageEmpty"

    def __init__(self, *, id: int) -> None:
        self.id = id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        return WebPageEmpty(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        return data.getvalue()
