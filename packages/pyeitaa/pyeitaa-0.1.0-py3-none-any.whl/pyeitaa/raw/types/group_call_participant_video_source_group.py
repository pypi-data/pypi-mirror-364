from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GroupCallParticipantVideoSourceGroup(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.GroupCallParticipantVideoSourceGroup`.

    Details:
        - Layer: ``135``
        - ID: ``-0x234ee749``

    Parameters:
        semantics: ``str``
        sources: List of ``int`` ``32-bit``
    """

    __slots__: List[str] = ["semantics", "sources"]

    ID = -0x234ee749
    QUALNAME = "types.GroupCallParticipantVideoSourceGroup"

    def __init__(self, *, semantics: str, sources: List[int]) -> None:
        self.semantics = semantics  # string
        self.sources = sources  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        semantics = String.read(data)
        
        sources = TLObject.read(data, Int)
        
        return GroupCallParticipantVideoSourceGroup(semantics=semantics, sources=sources)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.semantics))
        
        data.write(Vector(self.sources, Int))
        
        return data.getvalue()
