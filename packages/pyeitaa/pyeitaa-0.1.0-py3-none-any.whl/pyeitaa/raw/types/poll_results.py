from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PollResults(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PollResults`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2347d15d``

    Parameters:
        min (optional): ``bool``
        results (optional): List of :obj:`PollAnswerVoters <pyeitaa.raw.base.PollAnswerVoters>`
        total_voters (optional): ``int`` ``32-bit``
        recent_voters (optional): List of ``int`` ``64-bit``
        solution (optional): ``str``
        solution_entities (optional): List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`
    """

    __slots__: List[str] = ["min", "results", "total_voters", "recent_voters", "solution", "solution_entities"]

    ID = -0x2347d15d
    QUALNAME = "types.PollResults"

    def __init__(self, *, min: Optional[bool] = None, results: Optional[List["raw.base.PollAnswerVoters"]] = None, total_voters: Optional[int] = None, recent_voters: Optional[List[int]] = None, solution: Optional[str] = None, solution_entities: Optional[List["raw.base.MessageEntity"]] = None) -> None:
        self.min = min  # flags.0?true
        self.results = results  # flags.1?Vector<PollAnswerVoters>
        self.total_voters = total_voters  # flags.2?int
        self.recent_voters = recent_voters  # flags.3?Vector<long>
        self.solution = solution  # flags.4?string
        self.solution_entities = solution_entities  # flags.4?Vector<MessageEntity>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        min = True if flags & (1 << 0) else False
        results = TLObject.read(data) if flags & (1 << 1) else []
        
        total_voters = Int.read(data) if flags & (1 << 2) else None
        recent_voters = TLObject.read(data, Long) if flags & (1 << 3) else []
        
        solution = String.read(data) if flags & (1 << 4) else None
        solution_entities = TLObject.read(data) if flags & (1 << 4) else []
        
        return PollResults(min=min, results=results, total_voters=total_voters, recent_voters=recent_voters, solution=solution, solution_entities=solution_entities)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.min else 0
        flags |= (1 << 1) if self.results is not None else 0
        flags |= (1 << 2) if self.total_voters is not None else 0
        flags |= (1 << 3) if self.recent_voters is not None else 0
        flags |= (1 << 4) if self.solution is not None else 0
        flags |= (1 << 4) if self.solution_entities is not None else 0
        data.write(Int(flags))
        
        if self.results is not None:
            data.write(Vector(self.results))
        
        if self.total_voters is not None:
            data.write(Int(self.total_voters))
        
        if self.recent_voters is not None:
            data.write(Vector(self.recent_voters, Long))
        
        if self.solution is not None:
            data.write(String(self.solution))
        
        if self.solution_entities is not None:
            data.write(Vector(self.solution_entities))
        
        return data.getvalue()
