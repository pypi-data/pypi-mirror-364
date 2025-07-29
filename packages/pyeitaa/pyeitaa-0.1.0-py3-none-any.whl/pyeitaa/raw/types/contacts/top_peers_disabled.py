from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class TopPeersDisabled(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.contacts.TopPeers`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4ad36c63``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.GetTopPeers <pyeitaa.raw.functions.contacts.GetTopPeers>`
    """

    __slots__: List[str] = []

    ID = -0x4ad36c63
    QUALNAME = "types.contacts.TopPeersDisabled"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return TopPeersDisabled()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
