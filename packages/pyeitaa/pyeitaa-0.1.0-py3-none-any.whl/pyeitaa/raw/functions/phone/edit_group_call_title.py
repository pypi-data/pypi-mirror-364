from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EditGroupCallTitle(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1ca6ac0a``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        title: ``str``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["call", "title"]

    ID = 0x1ca6ac0a
    QUALNAME = "functions.phone.EditGroupCallTitle"

    def __init__(self, *, call: "raw.base.InputGroupCall", title: str) -> None:
        self.call = call  # InputGroupCall
        self.title = title  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        call = TLObject.read(data)
        
        title = String.read(data)
        
        return EditGroupCallTitle(call=call, title=title)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.call.write())
        
        data.write(String(self.title))
        
        return data.getvalue()
