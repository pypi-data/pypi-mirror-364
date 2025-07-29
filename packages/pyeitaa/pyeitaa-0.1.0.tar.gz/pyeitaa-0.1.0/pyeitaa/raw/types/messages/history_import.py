from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class HistoryImport(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.HistoryImport`.

    Details:
        - Layer: ``135``
        - ID: ``0x1662af0b``

    Parameters:
        id: ``int`` ``64-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.InitHistoryImport <pyeitaa.raw.functions.messages.InitHistoryImport>`
    """

    __slots__: List[str] = ["id"]

    ID = 0x1662af0b
    QUALNAME = "types.messages.HistoryImport"

    def __init__(self, *, id: int) -> None:
        self.id = id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        return HistoryImport(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        return data.getvalue()
