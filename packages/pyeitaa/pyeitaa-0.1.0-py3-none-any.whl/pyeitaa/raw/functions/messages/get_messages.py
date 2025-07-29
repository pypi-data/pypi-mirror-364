from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetMessages(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x63c66506``

    Parameters:
        id: List of :obj:`InputMessage <pyeitaa.raw.base.InputMessage>`

    Returns:
        :obj:`messages.Messages <pyeitaa.raw.base.messages.Messages>`
    """

    __slots__: List[str] = ["id"]

    ID = 0x63c66506
    QUALNAME = "functions.messages.GetMessages"

    def __init__(self, *, id: List["raw.base.InputMessage"]) -> None:
        self.id = id  # Vector<InputMessage>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return GetMessages(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.id))
        
        return data.getvalue()
