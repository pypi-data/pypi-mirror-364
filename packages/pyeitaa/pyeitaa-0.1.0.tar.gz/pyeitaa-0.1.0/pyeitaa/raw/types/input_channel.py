from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputChannel(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputChannel`.

    Details:
        - Layer: ``135``
        - ID: ``-0xca513d8``

    Parameters:
        channel_id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["channel_id", "access_hash"]

    ID = -0xca513d8
    QUALNAME = "types.InputChannel"

    def __init__(self, *, channel_id: int, access_hash: int) -> None:
        self.channel_id = channel_id  # long
        self.access_hash = access_hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel_id = Long.read(data)
        
        access_hash = Long.read(data)
        
        return InputChannel(channel_id=channel_id, access_hash=access_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.channel_id))
        
        data.write(Long(self.access_hash))
        
        return data.getvalue()
