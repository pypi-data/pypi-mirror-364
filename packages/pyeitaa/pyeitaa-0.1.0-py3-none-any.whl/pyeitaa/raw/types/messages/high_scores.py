from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class HighScores(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.HighScores`.

    Details:
        - Layer: ``135``
        - ID: ``-0x65c40267``

    Parameters:
        scores: List of :obj:`HighScore <pyeitaa.raw.base.HighScore>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetGameHighScores <pyeitaa.raw.functions.messages.GetGameHighScores>`
            - :obj:`messages.GetInlineGameHighScores <pyeitaa.raw.functions.messages.GetInlineGameHighScores>`
    """

    __slots__: List[str] = ["scores", "users"]

    ID = -0x65c40267
    QUALNAME = "types.messages.HighScores"

    def __init__(self, *, scores: List["raw.base.HighScore"], users: List["raw.base.User"]) -> None:
        self.scores = scores  # Vector<HighScore>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        scores = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return HighScores(scores=scores, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.scores))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
