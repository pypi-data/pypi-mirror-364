from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EditPeerFolders(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x6847d0ab``

    Parameters:
        folder_peers: List of :obj:`InputFolderPeer <pyeitaa.raw.base.InputFolderPeer>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["folder_peers"]

    ID = 0x6847d0ab
    QUALNAME = "functions.folders.EditPeerFolders"

    def __init__(self, *, folder_peers: List["raw.base.InputFolderPeer"]) -> None:
        self.folder_peers = folder_peers  # Vector<InputFolderPeer>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        folder_peers = TLObject.read(data)
        
        return EditPeerFolders(folder_peers=folder_peers)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.folder_peers))
        
        return data.getvalue()
