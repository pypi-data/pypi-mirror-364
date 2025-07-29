from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class LatestBuildVersion(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.LatestBuildVersion`.

    Details:
        - Layer: ``135``
        - ID: ``-0xc24051b``

    Parameters:
        build_version: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`GetLatestBuildVersion <pyeitaa.raw.functions.GetLatestBuildVersion>`
    """

    __slots__: List[str] = ["build_version"]

    ID = -0xc24051b
    QUALNAME = "types.LatestBuildVersion"

    def __init__(self, *, build_version: int) -> None:
        self.build_version = build_version  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        build_version = Int.read(data)
        
        return LatestBuildVersion(build_version=build_version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.build_version))
        
        return data.getvalue()
