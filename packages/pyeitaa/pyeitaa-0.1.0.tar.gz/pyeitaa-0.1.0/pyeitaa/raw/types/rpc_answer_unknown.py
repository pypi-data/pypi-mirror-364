from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class RpcAnswerUnknown(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RpcDropAnswer`.

    Details:
        - Layer: ``135``
        - ID: ``0x5e2ad36e``

    **No parameters required.**

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`RpcDropAnswer <pyeitaa.raw.functions.RpcDropAnswer>`
            - :obj:`RpcDropAnswer <pyeitaa.raw.functions.RpcDropAnswer>`
    """

    __slots__: List[str] = []

    ID = 0x5e2ad36e
    QUALNAME = "types.RpcAnswerUnknown"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return RpcAnswerUnknown()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
