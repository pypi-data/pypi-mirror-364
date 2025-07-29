from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateNewEncryptedMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x12bcbd9a``

    Parameters:
        message: :obj:`EncryptedMessage <pyeitaa.raw.base.EncryptedMessage>`
        qts: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["message", "qts"]

    ID = 0x12bcbd9a
    QUALNAME = "types.UpdateNewEncryptedMessage"

    def __init__(self, *, message: "raw.base.EncryptedMessage", qts: int) -> None:
        self.message = message  # EncryptedMessage
        self.qts = qts  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        message = TLObject.read(data)
        
        qts = Int.read(data)
        
        return UpdateNewEncryptedMessage(message=message, qts=qts)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.message.write())
        
        data.write(Int(self.qts))
        
        return data.getvalue()
