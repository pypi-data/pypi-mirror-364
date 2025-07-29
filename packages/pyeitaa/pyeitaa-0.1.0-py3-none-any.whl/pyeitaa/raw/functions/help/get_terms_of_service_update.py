from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetTermsOfServiceUpdate(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x2ca51fd1``

    **No parameters required.**

    Returns:
        :obj:`help.TermsOfServiceUpdate <pyeitaa.raw.base.help.TermsOfServiceUpdate>`
    """

    __slots__: List[str] = []

    ID = 0x2ca51fd1
    QUALNAME = "functions.help.GetTermsOfServiceUpdate"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetTermsOfServiceUpdate()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
