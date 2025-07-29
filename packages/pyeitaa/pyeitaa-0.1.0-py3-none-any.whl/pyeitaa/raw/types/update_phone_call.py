from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdatePhoneCall(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x54f094e2``

    Parameters:
        phone_call: :obj:`PhoneCall <pyeitaa.raw.base.PhoneCall>`
    """

    __slots__: List[str] = ["phone_call"]

    ID = -0x54f094e2
    QUALNAME = "types.UpdatePhoneCall"

    def __init__(self, *, phone_call: "raw.base.PhoneCall") -> None:
        self.phone_call = phone_call  # PhoneCall

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone_call = TLObject.read(data)
        
        return UpdatePhoneCall(phone_call=phone_call)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.phone_call.write())
        
        return data.getvalue()
