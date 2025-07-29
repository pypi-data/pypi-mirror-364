from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DhConfigNotModified(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.DhConfig`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3f1db9cb``

    Parameters:
        random: ``bytes``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetDhConfig <pyeitaa.raw.functions.messages.GetDhConfig>`
    """

    __slots__: List[str] = ["random"]

    ID = -0x3f1db9cb
    QUALNAME = "types.messages.DhConfigNotModified"

    def __init__(self, *, random: bytes) -> None:
        self.random = random  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        random = Bytes.read(data)
        
        return DhConfigNotModified(random=random)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.random))
        
        return data.getvalue()
