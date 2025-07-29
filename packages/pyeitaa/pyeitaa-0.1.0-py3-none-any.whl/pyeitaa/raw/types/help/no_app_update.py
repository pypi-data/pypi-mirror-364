from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class NoAppUpdate(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.AppUpdate`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3ba59aca``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetAppUpdate <pyeitaa.raw.functions.help.GetAppUpdate>`
    """

    __slots__: List[str] = []

    ID = -0x3ba59aca
    QUALNAME = "types.help.NoAppUpdate"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return NoAppUpdate()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
