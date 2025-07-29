from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DestroySession(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x18aededa``

    Parameters:
        session_id: ``int`` ``64-bit``

    Returns:
        :obj:`DestroySessionRes <pyeitaa.raw.base.DestroySessionRes>`
    """

    __slots__: List[str] = ["session_id"]

    ID = -0x18aededa
    QUALNAME = "functions.DestroySession"

    def __init__(self, *, session_id: int) -> None:
        self.session_id = session_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        session_id = Long.read(data)
        
        return DestroySession(session_id=session_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.session_id))
        
        return data.getvalue()
