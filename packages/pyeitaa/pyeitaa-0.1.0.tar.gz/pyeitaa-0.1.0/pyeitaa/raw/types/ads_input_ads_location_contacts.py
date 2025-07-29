from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class AdsInputAdsLocationContacts(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.AdsLocation`.

    Details:
        - Layer: ``135``
        - ID: ``-0x18bfa9bd``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x18bfa9bd
    QUALNAME = "types.AdsInputAdsLocationContacts"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return AdsInputAdsLocationContacts()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
