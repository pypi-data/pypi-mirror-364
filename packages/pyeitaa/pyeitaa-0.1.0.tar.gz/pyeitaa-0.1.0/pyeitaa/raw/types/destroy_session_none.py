from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DestroySessionNone(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DestroySessionRes`.

    Details:
        - Layer: ``135``
        - ID: ``0x62d350c9``

    Parameters:
        session_id: ``int`` ``64-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`DestroySession <pyeitaa.raw.functions.DestroySession>`
            - :obj:`DestroySession <pyeitaa.raw.functions.DestroySession>`
    """

    __slots__: List[str] = ["session_id"]

    ID = 0x62d350c9
    QUALNAME = "types.DestroySessionNone"

    def __init__(self, *, session_id: int) -> None:
        self.session_id = session_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        session_id = Long.read(data)
        
        return DestroySessionNone(session_id=session_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.session_id))
        
        return data.getvalue()
