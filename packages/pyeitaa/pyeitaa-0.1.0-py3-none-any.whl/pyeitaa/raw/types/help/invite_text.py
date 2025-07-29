from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InviteText(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.InviteText`.

    Details:
        - Layer: ``135``
        - ID: ``0x18cb9f78``

    Parameters:
        message: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetInviteText <pyeitaa.raw.functions.help.GetInviteText>`
    """

    __slots__: List[str] = ["message"]

    ID = 0x18cb9f78
    QUALNAME = "types.help.InviteText"

    def __init__(self, *, message: str) -> None:
        self.message = message  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        message = String.read(data)
        
        return InviteText(message=message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.message))
        
        return data.getvalue()
