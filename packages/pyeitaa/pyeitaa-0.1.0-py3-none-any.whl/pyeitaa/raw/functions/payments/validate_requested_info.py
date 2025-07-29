from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ValidateRequestedInfo(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x24efce90``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        msg_id: ``int`` ``32-bit``
        info: :obj:`PaymentRequestedInfo <pyeitaa.raw.base.PaymentRequestedInfo>`
        save (optional): ``bool``

    Returns:
        :obj:`payments.ValidatedRequestedInfo <pyeitaa.raw.base.payments.ValidatedRequestedInfo>`
    """

    __slots__: List[str] = ["peer", "msg_id", "info", "save"]

    ID = -0x24efce90
    QUALNAME = "functions.payments.ValidateRequestedInfo"

    def __init__(self, *, peer: "raw.base.InputPeer", msg_id: int, info: "raw.base.PaymentRequestedInfo", save: Optional[bool] = None) -> None:
        self.peer = peer  # InputPeer
        self.msg_id = msg_id  # int
        self.info = info  # PaymentRequestedInfo
        self.save = save  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        save = True if flags & (1 << 0) else False
        peer = TLObject.read(data)
        
        msg_id = Int.read(data)
        
        info = TLObject.read(data)
        
        return ValidateRequestedInfo(peer=peer, msg_id=msg_id, info=info, save=save)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.save else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Int(self.msg_id))
        
        data.write(self.info.write())
        
        return data.getvalue()
