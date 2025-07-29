from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputFolderPeer(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputFolderPeer`.

    Details:
        - Layer: ``135``
        - ID: ``-0x42d3d6a``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        folder_id: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["peer", "folder_id"]

    ID = -0x42d3d6a
    QUALNAME = "types.InputFolderPeer"

    def __init__(self, *, peer: "raw.base.InputPeer", folder_id: int) -> None:
        self.peer = peer  # InputPeer
        self.folder_id = folder_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        folder_id = Int.read(data)
        
        return InputFolderPeer(peer=peer, folder_id=folder_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.folder_id))
        
        return data.getvalue()
