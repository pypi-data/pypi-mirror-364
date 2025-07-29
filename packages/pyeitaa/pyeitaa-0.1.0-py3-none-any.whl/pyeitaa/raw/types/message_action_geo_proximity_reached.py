from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageActionGeoProximityReached(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x671f2969``

    Parameters:
        from_id: :obj:`Peer <pyeitaa.raw.base.Peer>`
        to_id: :obj:`Peer <pyeitaa.raw.base.Peer>`
        distance: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["from_id", "to_id", "distance"]

    ID = -0x671f2969
    QUALNAME = "types.MessageActionGeoProximityReached"

    def __init__(self, *, from_id: "raw.base.Peer", to_id: "raw.base.Peer", distance: int) -> None:
        self.from_id = from_id  # Peer
        self.to_id = to_id  # Peer
        self.distance = distance  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        from_id = TLObject.read(data)
        
        to_id = TLObject.read(data)
        
        distance = Int.read(data)
        
        return MessageActionGeoProximityReached(from_id=from_id, to_id=to_id, distance=distance)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.from_id.write())
        
        data.write(self.to_id.write())
        
        data.write(Int(self.distance))
        
        return data.getvalue()
