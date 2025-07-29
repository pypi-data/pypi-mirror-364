from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GetLocated(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x2cb743bc``

    Parameters:
        geo_point: :obj:`InputGeoPoint <pyeitaa.raw.base.InputGeoPoint>`
        background (optional): ``bool``
        self_expires (optional): ``int`` ``32-bit``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["geo_point", "background", "self_expires"]

    ID = -0x2cb743bc
    QUALNAME = "functions.contacts.GetLocated"

    def __init__(self, *, geo_point: "raw.base.InputGeoPoint", background: Optional[bool] = None, self_expires: Optional[int] = None) -> None:
        self.geo_point = geo_point  # InputGeoPoint
        self.background = background  # flags.1?true
        self.self_expires = self_expires  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        background = True if flags & (1 << 1) else False
        geo_point = TLObject.read(data)
        
        self_expires = Int.read(data) if flags & (1 << 0) else None
        return GetLocated(geo_point=geo_point, background=background, self_expires=self_expires)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.background else 0
        flags |= (1 << 0) if self.self_expires is not None else 0
        data.write(Int(flags))
        
        data.write(self.geo_point.write())
        
        if self.self_expires is not None:
            data.write(Int(self.self_expires))
        
        return data.getvalue()
