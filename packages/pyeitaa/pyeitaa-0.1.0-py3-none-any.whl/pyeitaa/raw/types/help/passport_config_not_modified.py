from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PassportConfigNotModified(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.PassportConfig`.

    Details:
        - Layer: ``135``
        - ID: ``-0x40460ba9``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetPassportConfig <pyeitaa.raw.functions.help.GetPassportConfig>`
    """

    __slots__: List[str] = []

    ID = -0x40460ba9
    QUALNAME = "types.help.PassportConfigNotModified"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return PassportConfigNotModified()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
