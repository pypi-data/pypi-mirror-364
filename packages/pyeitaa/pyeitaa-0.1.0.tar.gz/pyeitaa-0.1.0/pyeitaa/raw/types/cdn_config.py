from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class CdnConfig(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.CdnConfig`.

    Details:
        - Layer: ``135``
        - ID: ``0x5725e40a``

    Parameters:
        public_keys: List of :obj:`CdnPublicKey <pyeitaa.raw.base.CdnPublicKey>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetCdnConfig <pyeitaa.raw.functions.help.GetCdnConfig>`
    """

    __slots__: List[str] = ["public_keys"]

    ID = 0x5725e40a
    QUALNAME = "types.CdnConfig"

    def __init__(self, *, public_keys: List["raw.base.CdnPublicKey"]) -> None:
        self.public_keys = public_keys  # Vector<CdnPublicKey>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        public_keys = TLObject.read(data)
        
        return CdnConfig(public_keys=public_keys)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.public_keys))
        
        return data.getvalue()
