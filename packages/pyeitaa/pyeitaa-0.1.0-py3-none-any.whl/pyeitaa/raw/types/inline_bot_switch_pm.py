from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InlineBotSwitchPM(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InlineBotSwitchPM`.

    Details:
        - Layer: ``135``
        - ID: ``0x3c20629f``

    Parameters:
        text: ``str``
        start_param: ``str``
    """

    __slots__: List[str] = ["text", "start_param"]

    ID = 0x3c20629f
    QUALNAME = "types.InlineBotSwitchPM"

    def __init__(self, *, text: str, start_param: str) -> None:
        self.text = text  # string
        self.start_param = start_param  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        text = String.read(data)
        
        start_param = String.read(data)
        
        return InlineBotSwitchPM(text=text, start_param=start_param)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.text))
        
        data.write(String(self.start_param))
        
        return data.getvalue()
