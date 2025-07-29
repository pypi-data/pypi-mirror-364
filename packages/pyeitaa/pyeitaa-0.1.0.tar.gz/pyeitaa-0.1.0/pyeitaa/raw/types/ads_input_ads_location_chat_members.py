from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AdsInputAdsLocationChatMembers(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.AdsLocation`.

    Details:
        - Layer: ``135``
        - ID: ``-0x14323dbd``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
    """

    __slots__: List[str] = ["peer"]

    ID = -0x14323dbd
    QUALNAME = "types.AdsInputAdsLocationChatMembers"

    def __init__(self, *, peer: "raw.base.InputPeer") -> None:
        self.peer = peer  # InputPeer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        return AdsInputAdsLocationChatMembers(peer=peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        return data.getvalue()
