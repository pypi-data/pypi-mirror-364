from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PaymentForm(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.payments.PaymentForm`.

    Details:
        - Layer: ``135``
        - ID: ``0x1694761b``

    Parameters:
        form_id: ``int`` ``64-bit``
        bot_id: ``int`` ``64-bit``
        invoice: :obj:`Invoice <pyeitaa.raw.base.Invoice>`
        provider_id: ``int`` ``64-bit``
        url: ``str``
        users: List of :obj:`User <pyeitaa.raw.base.User>`
        can_save_credentials (optional): ``bool``
        password_missing (optional): ``bool``
        native_provider (optional): ``str``
        native_params (optional): :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
        saved_info (optional): :obj:`PaymentRequestedInfo <pyeitaa.raw.base.PaymentRequestedInfo>`
        saved_credentials (optional): :obj:`PaymentSavedCredentials <pyeitaa.raw.base.PaymentSavedCredentials>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.GetPaymentForm <pyeitaa.raw.functions.payments.GetPaymentForm>`
    """

    __slots__: List[str] = ["form_id", "bot_id", "invoice", "provider_id", "url", "users", "can_save_credentials", "password_missing", "native_provider", "native_params", "saved_info", "saved_credentials"]

    ID = 0x1694761b
    QUALNAME = "types.payments.PaymentForm"

    def __init__(self, *, form_id: int, bot_id: int, invoice: "raw.base.Invoice", provider_id: int, url: str, users: List["raw.base.User"], can_save_credentials: Optional[bool] = None, password_missing: Optional[bool] = None, native_provider: Optional[str] = None, native_params: "raw.base.DataJSON" = None, saved_info: "raw.base.PaymentRequestedInfo" = None, saved_credentials: "raw.base.PaymentSavedCredentials" = None) -> None:
        self.form_id = form_id  # long
        self.bot_id = bot_id  # long
        self.invoice = invoice  # Invoice
        self.provider_id = provider_id  # long
        self.url = url  # string
        self.users = users  # Vector<User>
        self.can_save_credentials = can_save_credentials  # flags.2?true
        self.password_missing = password_missing  # flags.3?true
        self.native_provider = native_provider  # flags.4?string
        self.native_params = native_params  # flags.4?DataJSON
        self.saved_info = saved_info  # flags.0?PaymentRequestedInfo
        self.saved_credentials = saved_credentials  # flags.1?PaymentSavedCredentials

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        can_save_credentials = True if flags & (1 << 2) else False
        password_missing = True if flags & (1 << 3) else False
        form_id = Long.read(data)
        
        bot_id = Long.read(data)
        
        invoice = TLObject.read(data)
        
        provider_id = Long.read(data)
        
        url = String.read(data)
        
        native_provider = String.read(data) if flags & (1 << 4) else None
        native_params = TLObject.read(data) if flags & (1 << 4) else None
        
        saved_info = TLObject.read(data) if flags & (1 << 0) else None
        
        saved_credentials = TLObject.read(data) if flags & (1 << 1) else None
        
        users = TLObject.read(data)
        
        return PaymentForm(form_id=form_id, bot_id=bot_id, invoice=invoice, provider_id=provider_id, url=url, users=users, can_save_credentials=can_save_credentials, password_missing=password_missing, native_provider=native_provider, native_params=native_params, saved_info=saved_info, saved_credentials=saved_credentials)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 2) if self.can_save_credentials else 0
        flags |= (1 << 3) if self.password_missing else 0
        flags |= (1 << 4) if self.native_provider is not None else 0
        flags |= (1 << 4) if self.native_params is not None else 0
        flags |= (1 << 0) if self.saved_info is not None else 0
        flags |= (1 << 1) if self.saved_credentials is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.form_id))
        
        data.write(Long(self.bot_id))
        
        data.write(self.invoice.write())
        
        data.write(Long(self.provider_id))
        
        data.write(String(self.url))
        
        if self.native_provider is not None:
            data.write(String(self.native_provider))
        
        if self.native_params is not None:
            data.write(self.native_params.write())
        
        if self.saved_info is not None:
            data.write(self.saved_info.write())
        
        if self.saved_credentials is not None:
            data.write(self.saved_credentials.write())
        
        data.write(Vector(self.users))
        
        return data.getvalue()
