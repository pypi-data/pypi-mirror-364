from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DestroyAuthKeyFail(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DestroyAuthKeyRes`.

    Details:
        - Layer: ``135``
        - ID: ``-0x15ef64ed``

    **No parameters required.**

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`DestroyAuthKey <pyeitaa.raw.functions.DestroyAuthKey>`
            - :obj:`DestroyAuthKey <pyeitaa.raw.functions.DestroyAuthKey>`
    """

    __slots__: List[str] = []

    ID = -0x15ef64ed
    QUALNAME = "types.DestroyAuthKeyFail"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return DestroyAuthKeyFail()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
