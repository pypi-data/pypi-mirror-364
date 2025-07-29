from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SendMessageUploadAudioAction(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SendMessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0xcae2855``

    Parameters:
        progress: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["progress"]

    ID = -0xcae2855
    QUALNAME = "types.SendMessageUploadAudioAction"

    def __init__(self, *, progress: int) -> None:
        self.progress = progress  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        progress = Int.read(data)
        
        return SendMessageUploadAudioAction(progress=progress)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.progress))
        
        return data.getvalue()
