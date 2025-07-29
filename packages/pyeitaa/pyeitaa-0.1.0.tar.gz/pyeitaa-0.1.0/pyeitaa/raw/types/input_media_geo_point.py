from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputMediaGeoPoint(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x63bbebc``

    Parameters:
        geo_point: :obj:`InputGeoPoint <pyeitaa.raw.base.InputGeoPoint>`
    """

    __slots__: List[str] = ["geo_point"]

    ID = -0x63bbebc
    QUALNAME = "types.InputMediaGeoPoint"

    def __init__(self, *, geo_point: "raw.base.InputGeoPoint") -> None:
        self.geo_point = geo_point  # InputGeoPoint

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        geo_point = TLObject.read(data)
        
        return InputMediaGeoPoint(geo_point=geo_point)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.geo_point.write())
        
        return data.getvalue()
