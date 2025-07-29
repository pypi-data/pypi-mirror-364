from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateStatus(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x6628562c``

    Parameters:
        offline: ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["offline"]

    ID = 0x6628562c
    QUALNAME = "functions.account.UpdateStatus"

    def __init__(self, *, offline: bool) -> None:
        self.offline = offline  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        offline = Bool.read(data)
        
        return UpdateStatus(offline=offline)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bool(self.offline))
        
        return data.getvalue()
