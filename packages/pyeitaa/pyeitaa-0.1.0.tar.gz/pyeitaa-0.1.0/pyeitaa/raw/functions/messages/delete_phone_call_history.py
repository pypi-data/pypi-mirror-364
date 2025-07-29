from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class DeletePhoneCallHistory(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x6341bf7``

    Parameters:
        revoke (optional): ``bool``

    Returns:
        :obj:`messages.AffectedFoundMessages <pyeitaa.raw.base.messages.AffectedFoundMessages>`
    """

    __slots__: List[str] = ["revoke"]

    ID = -0x6341bf7
    QUALNAME = "functions.messages.DeletePhoneCallHistory"

    def __init__(self, *, revoke: Optional[bool] = None) -> None:
        self.revoke = revoke  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        revoke = True if flags & (1 << 0) else False
        return DeletePhoneCallHistory(revoke=revoke)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.revoke else 0
        data.write(Int(flags))
        
        return data.getvalue()
