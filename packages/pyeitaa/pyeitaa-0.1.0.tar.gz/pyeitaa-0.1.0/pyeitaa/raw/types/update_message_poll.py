from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateMessagePoll(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x535e9a85``

    Parameters:
        poll_id: ``int`` ``64-bit``
        results: :obj:`PollResults <pyeitaa.raw.base.PollResults>`
        poll (optional): :obj:`Poll <pyeitaa.raw.base.Poll>`
    """

    __slots__: List[str] = ["poll_id", "results", "poll"]

    ID = -0x535e9a85
    QUALNAME = "types.UpdateMessagePoll"

    def __init__(self, *, poll_id: int, results: "raw.base.PollResults", poll: "raw.base.Poll" = None) -> None:
        self.poll_id = poll_id  # long
        self.results = results  # PollResults
        self.poll = poll  # flags.0?Poll

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        poll_id = Long.read(data)
        
        poll = TLObject.read(data) if flags & (1 << 0) else None
        
        results = TLObject.read(data)
        
        return UpdateMessagePoll(poll_id=poll_id, results=results, poll=poll)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.poll is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.poll_id))
        
        if self.poll is not None:
            data.write(self.poll.write())
        
        data.write(self.results.write())
        
        return data.getvalue()
