from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UrlAuthResultDefault(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.UrlAuthResult`.

    Details:
        - Layer: ``135``
        - ID: ``-0x562924e1``

    **No parameters required.**

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.RequestUrlAuth <pyeitaa.raw.functions.messages.RequestUrlAuth>`
            - :obj:`messages.AcceptUrlAuth <pyeitaa.raw.functions.messages.AcceptUrlAuth>`
    """

    __slots__: List[str] = []

    ID = -0x562924e1
    QUALNAME = "types.UrlAuthResultDefault"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return UrlAuthResultDefault()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
