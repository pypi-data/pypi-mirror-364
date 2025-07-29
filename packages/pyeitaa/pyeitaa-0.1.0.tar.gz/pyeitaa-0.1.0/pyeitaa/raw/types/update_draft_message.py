from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateDraftMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x11d44697``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        draft: :obj:`DraftMessage <pyeitaa.raw.base.DraftMessage>`
    """

    __slots__: List[str] = ["peer", "draft"]

    ID = -0x11d44697
    QUALNAME = "types.UpdateDraftMessage"

    def __init__(self, *, peer: "raw.base.Peer", draft: "raw.base.DraftMessage") -> None:
        self.peer = peer  # Peer
        self.draft = draft  # DraftMessage

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        draft = TLObject.read(data)
        
        return UpdateDraftMessage(peer=peer, draft=draft)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.draft.write())
        
        return data.getvalue()
