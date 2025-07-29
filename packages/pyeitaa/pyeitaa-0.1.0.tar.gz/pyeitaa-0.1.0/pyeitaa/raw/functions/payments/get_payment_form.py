from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetPaymentForm(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x75ccc373``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        msg_id: ``int`` ``32-bit``
        theme_params (optional): :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`

    Returns:
        :obj:`payments.PaymentForm <pyeitaa.raw.base.payments.PaymentForm>`
    """

    __slots__: List[str] = ["peer", "msg_id", "theme_params"]

    ID = -0x75ccc373
    QUALNAME = "functions.payments.GetPaymentForm"

    def __init__(self, *, peer: "raw.base.InputPeer", msg_id: int, theme_params: "raw.base.DataJSON" = None) -> None:
        self.peer = peer  # InputPeer
        self.msg_id = msg_id  # int
        self.theme_params = theme_params  # flags.0?DataJSON

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        peer = TLObject.read(data)
        
        msg_id = Int.read(data)
        
        theme_params = TLObject.read(data) if flags & (1 << 0) else None
        
        return GetPaymentForm(peer=peer, msg_id=msg_id, theme_params=theme_params)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.theme_params is not None else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Int(self.msg_id))
        
        if self.theme_params is not None:
            data.write(self.theme_params.write())
        
        return data.getvalue()
