from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class DialogPeer(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DialogPeer`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1a9240fb``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetDialogUnreadMarks <pyeitaa.raw.functions.messages.GetDialogUnreadMarks>`
    """

    __slots__: List[str] = ["peer"]

    ID = -0x1a9240fb
    QUALNAME = "types.DialogPeer"

    def __init__(self, *, peer: "raw.base.Peer") -> None:
        self.peer = peer  # Peer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        return DialogPeer(peer=peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        return data.getvalue()
