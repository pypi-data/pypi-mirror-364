from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SendPaymentForm(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x30c3bc9d``

    Parameters:
        form_id: ``int`` ``64-bit``
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        msg_id: ``int`` ``32-bit``
        credentials: :obj:`InputPaymentCredentials <pyeitaa.raw.base.InputPaymentCredentials>`
        requested_info_id (optional): ``str``
        shipping_option_id (optional): ``str``
        tip_amount (optional): ``int`` ``64-bit``

    Returns:
        :obj:`payments.PaymentResult <pyeitaa.raw.base.payments.PaymentResult>`
    """

    __slots__: List[str] = ["form_id", "peer", "msg_id", "credentials", "requested_info_id", "shipping_option_id", "tip_amount"]

    ID = 0x30c3bc9d
    QUALNAME = "functions.payments.SendPaymentForm"

    def __init__(self, *, form_id: int, peer: "raw.base.InputPeer", msg_id: int, credentials: "raw.base.InputPaymentCredentials", requested_info_id: Optional[str] = None, shipping_option_id: Optional[str] = None, tip_amount: Optional[int] = None) -> None:
        self.form_id = form_id  # long
        self.peer = peer  # InputPeer
        self.msg_id = msg_id  # int
        self.credentials = credentials  # InputPaymentCredentials
        self.requested_info_id = requested_info_id  # flags.0?string
        self.shipping_option_id = shipping_option_id  # flags.1?string
        self.tip_amount = tip_amount  # flags.2?long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        form_id = Long.read(data)
        
        peer = TLObject.read(data)
        
        msg_id = Int.read(data)
        
        requested_info_id = String.read(data) if flags & (1 << 0) else None
        shipping_option_id = String.read(data) if flags & (1 << 1) else None
        credentials = TLObject.read(data)
        
        tip_amount = Long.read(data) if flags & (1 << 2) else None
        return SendPaymentForm(form_id=form_id, peer=peer, msg_id=msg_id, credentials=credentials, requested_info_id=requested_info_id, shipping_option_id=shipping_option_id, tip_amount=tip_amount)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.requested_info_id is not None else 0
        flags |= (1 << 1) if self.shipping_option_id is not None else 0
        flags |= (1 << 2) if self.tip_amount is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.form_id))
        
        data.write(self.peer.write())
        
        data.write(Int(self.msg_id))
        
        if self.requested_info_id is not None:
            data.write(String(self.requested_info_id))
        
        if self.shipping_option_id is not None:
            data.write(String(self.shipping_option_id))
        
        data.write(self.credentials.write())
        
        if self.tip_amount is not None:
            data.write(Long(self.tip_amount))
        
        return data.getvalue()
