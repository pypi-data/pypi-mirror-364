from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageInteractionCounters(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageInteractionCounters`.

    Details:
        - Layer: ``135``
        - ID: ``-0x52b03643``

    Parameters:
        msg_id: ``int`` ``32-bit``
        views: ``int`` ``32-bit``
        forwards: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["msg_id", "views", "forwards"]

    ID = -0x52b03643
    QUALNAME = "types.MessageInteractionCounters"

    def __init__(self, *, msg_id: int, views: int, forwards: int) -> None:
        self.msg_id = msg_id  # int
        self.views = views  # int
        self.forwards = forwards  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        msg_id = Int.read(data)
        
        views = Int.read(data)
        
        forwards = Int.read(data)
        
        return MessageInteractionCounters(msg_id=msg_id, views=views, forwards=forwards)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.msg_id))
        
        data.write(Int(self.views))
        
        data.write(Int(self.forwards))
        
        return data.getvalue()
