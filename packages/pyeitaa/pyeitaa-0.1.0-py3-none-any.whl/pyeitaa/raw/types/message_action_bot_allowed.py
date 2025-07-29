from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageActionBotAllowed(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x54165002``

    Parameters:
        domain: ``str``
    """

    __slots__: List[str] = ["domain"]

    ID = -0x54165002
    QUALNAME = "types.MessageActionBotAllowed"

    def __init__(self, *, domain: str) -> None:
        self.domain = domain  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        domain = String.read(data)
        
        return MessageActionBotAllowed(domain=domain)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.domain))
        
        return data.getvalue()
