from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ExportedGroupCallInvite(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.phone.ExportedGroupCallInvite`.

    Details:
        - Layer: ``135``
        - ID: ``0x204bd158``

    Parameters:
        link: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`phone.ExportGroupCallInvite <pyeitaa.raw.functions.phone.ExportGroupCallInvite>`
    """

    __slots__: List[str] = ["link"]

    ID = 0x204bd158
    QUALNAME = "types.phone.ExportedGroupCallInvite"

    def __init__(self, *, link: str) -> None:
        self.link = link  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        link = String.read(data)
        
        return ExportedGroupCallInvite(link=link)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.link))
        
        return data.getvalue()
