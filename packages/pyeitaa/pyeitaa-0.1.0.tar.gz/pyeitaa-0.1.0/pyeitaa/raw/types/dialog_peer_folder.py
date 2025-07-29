from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DialogPeerFolder(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DialogPeer`.

    Details:
        - Layer: ``135``
        - ID: ``0x514519e2``

    Parameters:
        folder_id: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetDialogUnreadMarks <pyeitaa.raw.functions.messages.GetDialogUnreadMarks>`
    """

    __slots__: List[str] = ["folder_id"]

    ID = 0x514519e2
    QUALNAME = "types.DialogPeerFolder"

    def __init__(self, *, folder_id: int) -> None:
        self.folder_id = folder_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        folder_id = Int.read(data)
        
        return DialogPeerFolder(folder_id=folder_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.folder_id))
        
        return data.getvalue()
