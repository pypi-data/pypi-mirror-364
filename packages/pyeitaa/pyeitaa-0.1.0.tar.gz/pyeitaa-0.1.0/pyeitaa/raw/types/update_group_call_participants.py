from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateGroupCallParticipants(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0xd1424b2``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        participants: List of :obj:`GroupCallParticipant <pyeitaa.raw.base.GroupCallParticipant>`
        version: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["call", "participants", "version"]

    ID = -0xd1424b2
    QUALNAME = "types.UpdateGroupCallParticipants"

    def __init__(self, *, call: "raw.base.InputGroupCall", participants: List["raw.base.GroupCallParticipant"], version: int) -> None:
        self.call = call  # InputGroupCall
        self.participants = participants  # Vector<GroupCallParticipant>
        self.version = version  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        call = TLObject.read(data)
        
        participants = TLObject.read(data)
        
        version = Int.read(data)
        
        return UpdateGroupCallParticipants(call=call, participants=participants, version=version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.call.write())
        
        data.write(Vector(self.participants))
        
        data.write(Int(self.version))
        
        return data.getvalue()
