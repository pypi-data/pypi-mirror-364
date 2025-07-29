from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ToggleTopPeers(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x7aeb4226``

    Parameters:
        enabled: ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["enabled"]

    ID = -0x7aeb4226
    QUALNAME = "functions.contacts.ToggleTopPeers"

    def __init__(self, *, enabled: bool) -> None:
        self.enabled = enabled  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        enabled = Bool.read(data)
        
        return ToggleTopPeers(enabled=enabled)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bool(self.enabled))
        
        return data.getvalue()
