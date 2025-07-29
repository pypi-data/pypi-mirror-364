from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SentEncryptedFile(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.SentEncryptedMessage`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6b6c00ce``

    Parameters:
        date: ``int`` ``32-bit``
        file: :obj:`EncryptedFile <pyeitaa.raw.base.EncryptedFile>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.SendEncrypted <pyeitaa.raw.functions.messages.SendEncrypted>`
            - :obj:`messages.SendEncryptedFile <pyeitaa.raw.functions.messages.SendEncryptedFile>`
            - :obj:`messages.SendEncryptedService <pyeitaa.raw.functions.messages.SendEncryptedService>`
    """

    __slots__: List[str] = ["date", "file"]

    ID = -0x6b6c00ce
    QUALNAME = "types.messages.SentEncryptedFile"

    def __init__(self, *, date: int, file: "raw.base.EncryptedFile") -> None:
        self.date = date  # int
        self.file = file  # EncryptedFile

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        date = Int.read(data)
        
        file = TLObject.read(data)
        
        return SentEncryptedFile(date=date, file=file)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.date))
        
        data.write(self.file.write())
        
        return data.getvalue()
