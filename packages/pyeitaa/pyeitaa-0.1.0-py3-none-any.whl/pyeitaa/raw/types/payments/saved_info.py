from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SavedInfo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.payments.SavedInfo`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4701bc4``

    Parameters:
        has_saved_credentials (optional): ``bool``
        saved_info (optional): :obj:`PaymentRequestedInfo <pyeitaa.raw.base.PaymentRequestedInfo>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.GetSavedInfo <pyeitaa.raw.functions.payments.GetSavedInfo>`
    """

    __slots__: List[str] = ["has_saved_credentials", "saved_info"]

    ID = -0x4701bc4
    QUALNAME = "types.payments.SavedInfo"

    def __init__(self, *, has_saved_credentials: Optional[bool] = None, saved_info: "raw.base.PaymentRequestedInfo" = None) -> None:
        self.has_saved_credentials = has_saved_credentials  # flags.1?true
        self.saved_info = saved_info  # flags.0?PaymentRequestedInfo

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        has_saved_credentials = True if flags & (1 << 1) else False
        saved_info = TLObject.read(data) if flags & (1 << 0) else None
        
        return SavedInfo(has_saved_credentials=has_saved_credentials, saved_info=saved_info)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.has_saved_credentials else 0
        flags |= (1 << 0) if self.saved_info is not None else 0
        data.write(Int(flags))
        
        if self.saved_info is not None:
            data.write(self.saved_info.write())
        
        return data.getvalue()
