from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DeepLinkInfoEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.DeepLinkInfo`.

    Details:
        - Layer: ``135``
        - ID: ``0x66afa166``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetDeepLinkInfo <pyeitaa.raw.functions.help.GetDeepLinkInfo>`
    """

    __slots__: List[str] = []

    ID = 0x66afa166
    QUALNAME = "types.help.DeepLinkInfoEmpty"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return DeepLinkInfoEmpty()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
