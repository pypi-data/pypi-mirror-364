from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetGroupsForDiscussion(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xa252c88``

    **No parameters required.**

    Returns:
        :obj:`messages.Chats <pyeitaa.raw.base.messages.Chats>`
    """

    __slots__: List[str] = []

    ID = -0xa252c88
    QUALNAME = "functions.channels.GetGroupsForDiscussion"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetGroupsForDiscussion()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
