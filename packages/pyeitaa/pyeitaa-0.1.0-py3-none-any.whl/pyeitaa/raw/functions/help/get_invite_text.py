from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetInviteText(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x4d392343``

    **No parameters required.**

    Returns:
        :obj:`help.InviteText <pyeitaa.raw.base.help.InviteText>`
    """

    __slots__: List[str] = []

    ID = 0x4d392343
    QUALNAME = "functions.help.GetInviteText"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetInviteText()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
