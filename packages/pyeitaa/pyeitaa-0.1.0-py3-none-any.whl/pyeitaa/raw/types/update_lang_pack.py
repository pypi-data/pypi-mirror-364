from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateLangPack(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x56022f4d``

    Parameters:
        difference: :obj:`LangPackDifference <pyeitaa.raw.base.LangPackDifference>`
    """

    __slots__: List[str] = ["difference"]

    ID = 0x56022f4d
    QUALNAME = "types.UpdateLangPack"

    def __init__(self, *, difference: "raw.base.LangPackDifference") -> None:
        self.difference = difference  # LangPackDifference

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        difference = TLObject.read(data)
        
        return UpdateLangPack(difference=difference)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.difference.write())
        
        return data.getvalue()
