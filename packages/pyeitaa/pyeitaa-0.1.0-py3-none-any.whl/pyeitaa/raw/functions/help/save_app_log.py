from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SaveAppLog(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x6f02f748``

    Parameters:
        events: List of :obj:`InputAppEvent <pyeitaa.raw.base.InputAppEvent>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["events"]

    ID = 0x6f02f748
    QUALNAME = "functions.help.SaveAppLog"

    def __init__(self, *, events: List["raw.base.InputAppEvent"]) -> None:
        self.events = events  # Vector<InputAppEvent>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        events = TLObject.read(data)
        
        return SaveAppLog(events=events)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.events))
        
        return data.getvalue()
