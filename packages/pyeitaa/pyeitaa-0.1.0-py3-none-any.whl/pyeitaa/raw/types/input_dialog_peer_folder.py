from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputDialogPeerFolder(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputDialogPeer`.

    Details:
        - Layer: ``135``
        - ID: ``0x64600527``

    Parameters:
        folder_id: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["folder_id"]

    ID = 0x64600527
    QUALNAME = "types.InputDialogPeerFolder"

    def __init__(self, *, folder_id: int) -> None:
        self.folder_id = folder_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        folder_id = Int.read(data)
        
        return InputDialogPeerFolder(folder_id=folder_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.folder_id))
        
        return data.getvalue()
