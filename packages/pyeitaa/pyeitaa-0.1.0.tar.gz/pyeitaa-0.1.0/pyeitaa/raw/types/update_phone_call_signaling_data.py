from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdatePhoneCallSignalingData(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x2661bf09``

    Parameters:
        phone_call_id: ``int`` ``64-bit``
        data: ``bytes``
    """

    __slots__: List[str] = ["phone_call_id", "data"]

    ID = 0x2661bf09
    QUALNAME = "types.UpdatePhoneCallSignalingData"

    def __init__(self, *, phone_call_id: int, data: bytes) -> None:
        self.phone_call_id = phone_call_id  # long
        self.data = data  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone_call_id = Long.read(data)
        
        data = Bytes.read(data)
        
        return UpdatePhoneCallSignalingData(phone_call_id=phone_call_id, data=data)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.phone_call_id))
        
        data.write(Bytes(self.data))
        
        return data.getvalue()
