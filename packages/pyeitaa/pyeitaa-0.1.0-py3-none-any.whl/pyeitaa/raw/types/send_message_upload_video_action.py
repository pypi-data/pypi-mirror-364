from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SendMessageUploadVideoAction(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SendMessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1689c514``

    Parameters:
        progress: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["progress"]

    ID = -0x1689c514
    QUALNAME = "types.SendMessageUploadVideoAction"

    def __init__(self, *, progress: int) -> None:
        self.progress = progress  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        progress = Int.read(data)
        
        return SendMessageUploadVideoAction(progress=progress)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.progress))
        
        return data.getvalue()
