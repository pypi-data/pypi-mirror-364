from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class TermsOfServiceUpdate(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.TermsOfServiceUpdate`.

    Details:
        - Layer: ``135``
        - ID: ``0x28ecf961``

    Parameters:
        expires: ``int`` ``32-bit``
        terms_of_service: :obj:`help.TermsOfService <pyeitaa.raw.base.help.TermsOfService>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetTermsOfServiceUpdate <pyeitaa.raw.functions.help.GetTermsOfServiceUpdate>`
    """

    __slots__: List[str] = ["expires", "terms_of_service"]

    ID = 0x28ecf961
    QUALNAME = "types.help.TermsOfServiceUpdate"

    def __init__(self, *, expires: int, terms_of_service: "raw.base.help.TermsOfService") -> None:
        self.expires = expires  # int
        self.terms_of_service = terms_of_service  # help.TermsOfService

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        expires = Int.read(data)
        
        terms_of_service = TLObject.read(data)
        
        return TermsOfServiceUpdate(expires=expires, terms_of_service=terms_of_service)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.expires))
        
        data.write(self.terms_of_service.write())
        
        return data.getvalue()
