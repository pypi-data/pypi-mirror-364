from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetDialogUnreadMarks(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x22e24e22``

    **No parameters required.**

    Returns:
        List of :obj:`DialogPeer <pyeitaa.raw.base.DialogPeer>`
    """

    __slots__: List[str] = []

    ID = 0x22e24e22
    QUALNAME = "functions.messages.GetDialogUnreadMarks"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetDialogUnreadMarks()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
