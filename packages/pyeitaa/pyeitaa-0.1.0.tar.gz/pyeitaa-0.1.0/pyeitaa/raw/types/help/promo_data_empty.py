from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PromoDataEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.PromoData`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6709538b``

    Parameters:
        expires: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetPromoData <pyeitaa.raw.functions.help.GetPromoData>`
    """

    __slots__: List[str] = ["expires"]

    ID = -0x6709538b
    QUALNAME = "types.help.PromoDataEmpty"

    def __init__(self, *, expires: int) -> None:
        self.expires = expires  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        expires = Int.read(data)
        
        return PromoDataEmpty(expires=expires)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.expires))
        
        return data.getvalue()
