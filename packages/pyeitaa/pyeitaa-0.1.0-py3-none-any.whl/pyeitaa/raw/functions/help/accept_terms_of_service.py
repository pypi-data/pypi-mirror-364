from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AcceptTermsOfService(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x118d0866``

    Parameters:
        id: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["id"]

    ID = -0x118d0866
    QUALNAME = "functions.help.AcceptTermsOfService"

    def __init__(self, *, id: "raw.base.DataJSON") -> None:
        self.id = id  # DataJSON

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return AcceptTermsOfService(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.id.write())
        
        return data.getvalue()
