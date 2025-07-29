from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class GetAdminedPublicChannels(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x74fc951``

    Parameters:
        by_location (optional): ``bool``
        check_limit (optional): ``bool``

    Returns:
        :obj:`messages.Chats <pyeitaa.raw.base.messages.Chats>`
    """

    __slots__: List[str] = ["by_location", "check_limit"]

    ID = -0x74fc951
    QUALNAME = "functions.channels.GetAdminedPublicChannels"

    def __init__(self, *, by_location: Optional[bool] = None, check_limit: Optional[bool] = None) -> None:
        self.by_location = by_location  # flags.0?true
        self.check_limit = check_limit  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        by_location = True if flags & (1 << 0) else False
        check_limit = True if flags & (1 << 1) else False
        return GetAdminedPublicChannels(by_location=by_location, check_limit=check_limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.by_location else 0
        flags |= (1 << 1) if self.check_limit else 0
        data.write(Int(flags))
        
        return data.getvalue()
