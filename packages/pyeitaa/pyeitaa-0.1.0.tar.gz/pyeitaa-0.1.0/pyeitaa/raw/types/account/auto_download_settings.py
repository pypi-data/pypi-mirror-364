from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AutoDownloadSettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.AutoDownloadSettings`.

    Details:
        - Layer: ``135``
        - ID: ``0x63cacf26``

    Parameters:
        low: :obj:`AutoDownloadSettings <pyeitaa.raw.base.AutoDownloadSettings>`
        medium: :obj:`AutoDownloadSettings <pyeitaa.raw.base.AutoDownloadSettings>`
        high: :obj:`AutoDownloadSettings <pyeitaa.raw.base.AutoDownloadSettings>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetAutoDownloadSettings <pyeitaa.raw.functions.account.GetAutoDownloadSettings>`
    """

    __slots__: List[str] = ["low", "medium", "high"]

    ID = 0x63cacf26
    QUALNAME = "types.account.AutoDownloadSettings"

    def __init__(self, *, low: "raw.base.AutoDownloadSettings", medium: "raw.base.AutoDownloadSettings", high: "raw.base.AutoDownloadSettings") -> None:
        self.low = low  # AutoDownloadSettings
        self.medium = medium  # AutoDownloadSettings
        self.high = high  # AutoDownloadSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        low = TLObject.read(data)
        
        medium = TLObject.read(data)
        
        high = TLObject.read(data)
        
        return AutoDownloadSettings(low=low, medium=medium, high=high)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.low.write())
        
        data.write(self.medium.write())
        
        data.write(self.high.write())
        
        return data.getvalue()
