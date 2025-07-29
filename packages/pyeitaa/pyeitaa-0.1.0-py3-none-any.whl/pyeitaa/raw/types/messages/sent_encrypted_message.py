from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SentEncryptedMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.SentEncryptedMessage`.

    Details:
        - Layer: ``135``
        - ID: ``0x560f8935``

    Parameters:
        date: ``int`` ``32-bit``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.SendEncrypted <pyeitaa.raw.functions.messages.SendEncrypted>`
            - :obj:`messages.SendEncryptedFile <pyeitaa.raw.functions.messages.SendEncryptedFile>`
            - :obj:`messages.SendEncryptedService <pyeitaa.raw.functions.messages.SendEncryptedService>`
    """

    __slots__: List[str] = ["date"]

    ID = 0x560f8935
    QUALNAME = "types.messages.SentEncryptedMessage"

    def __init__(self, *, date: int) -> None:
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        date = Int.read(data)
        
        return SentEncryptedMessage(date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.date))
        
        return data.getvalue()
