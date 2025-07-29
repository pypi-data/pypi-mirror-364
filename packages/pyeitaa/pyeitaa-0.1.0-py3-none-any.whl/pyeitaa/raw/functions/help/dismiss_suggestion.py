from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class DismissSuggestion(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xaf2455f``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        suggestion: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "suggestion"]

    ID = -0xaf2455f
    QUALNAME = "functions.help.DismissSuggestion"

    def __init__(self, *, peer: "raw.base.InputPeer", suggestion: str) -> None:
        self.peer = peer  # InputPeer
        self.suggestion = suggestion  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        suggestion = String.read(data)
        
        return DismissSuggestion(peer=peer, suggestion=suggestion)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(String(self.suggestion))
        
        return data.getvalue()
