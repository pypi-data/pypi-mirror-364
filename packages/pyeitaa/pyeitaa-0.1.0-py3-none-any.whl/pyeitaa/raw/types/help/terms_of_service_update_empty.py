from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class TermsOfServiceUpdateEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.TermsOfServiceUpdate`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1ccf6081``

    Parameters:
        expires: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetTermsOfServiceUpdate <pyeitaa.raw.functions.help.GetTermsOfServiceUpdate>`
    """

    __slots__: List[str] = ["expires"]

    ID = -0x1ccf6081
    QUALNAME = "types.help.TermsOfServiceUpdateEmpty"

    def __init__(self, *, expires: int) -> None:
        self.expires = expires  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        expires = Int.read(data)
        
        return TermsOfServiceUpdateEmpty(expires=expires)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.expires))
        
        return data.getvalue()
