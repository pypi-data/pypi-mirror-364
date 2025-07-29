from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageMediaGeo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0x56e0d474``

    Parameters:
        geo: :obj:`GeoPoint <pyeitaa.raw.base.GeoPoint>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyeitaa.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyeitaa.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyeitaa.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["geo"]

    ID = 0x56e0d474
    QUALNAME = "types.MessageMediaGeo"

    def __init__(self, *, geo: "raw.base.GeoPoint") -> None:
        self.geo = geo  # GeoPoint

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        geo = TLObject.read(data)
        
        return MessageMediaGeo(geo=geo)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.geo.write())
        
        return data.getvalue()
