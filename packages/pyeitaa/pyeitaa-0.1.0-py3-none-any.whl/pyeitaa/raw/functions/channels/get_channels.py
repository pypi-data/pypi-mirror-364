from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetChannels(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0xa7f6bbb``

    Parameters:
        id: List of :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`

    Returns:
        :obj:`messages.Chats <pyeitaa.raw.base.messages.Chats>`
    """

    __slots__: List[str] = ["id"]

    ID = 0xa7f6bbb
    QUALNAME = "functions.channels.GetChannels"

    def __init__(self, *, id: List["raw.base.InputChannel"]) -> None:
        self.id = id  # Vector<InputChannel>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return GetChannels(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.id))
        
        return data.getvalue()
