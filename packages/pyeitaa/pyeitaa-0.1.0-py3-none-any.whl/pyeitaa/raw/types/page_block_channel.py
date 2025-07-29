from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageBlockChannel(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``-0x10e8ae4b``

    Parameters:
        channel: :obj:`Chat <pyeitaa.raw.base.Chat>`
    """

    __slots__: List[str] = ["channel"]

    ID = -0x10e8ae4b
    QUALNAME = "types.PageBlockChannel"

    def __init__(self, *, channel: "raw.base.Chat") -> None:
        self.channel = channel  # Chat

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        return PageBlockChannel(channel=channel)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        return data.getvalue()
