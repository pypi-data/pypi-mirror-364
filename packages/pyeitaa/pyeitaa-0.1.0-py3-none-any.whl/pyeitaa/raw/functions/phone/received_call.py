from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ReceivedCall(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x17d54f61``

    Parameters:
        peer: :obj:`InputPhoneCall <pyeitaa.raw.base.InputPhoneCall>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer"]

    ID = 0x17d54f61
    QUALNAME = "functions.phone.ReceivedCall"

    def __init__(self, *, peer: "raw.base.InputPhoneCall") -> None:
        self.peer = peer  # InputPhoneCall

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        return ReceivedCall(peer=peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        return data.getvalue()
