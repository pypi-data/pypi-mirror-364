from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SendSignalingData(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x856c7d``

    Parameters:
        peer: :obj:`InputPhoneCall <pyeitaa.raw.base.InputPhoneCall>`
        data: ``bytes``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "data"]

    ID = -0x856c7d
    QUALNAME = "functions.phone.SendSignalingData"

    def __init__(self, *, peer: "raw.base.InputPhoneCall", data: bytes) -> None:
        self.peer = peer  # InputPhoneCall
        self.data = data  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        data = Bytes.read(data)
        
        return SendSignalingData(peer=peer, data=data)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Bytes(self.data))
        
        return data.getvalue()
