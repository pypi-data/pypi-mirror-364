from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateLangPackTooLong(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x46560264``

    Parameters:
        lang_code: ``str``
    """

    __slots__: List[str] = ["lang_code"]

    ID = 0x46560264
    QUALNAME = "types.UpdateLangPackTooLong"

    def __init__(self, *, lang_code: str) -> None:
        self.lang_code = lang_code  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        lang_code = String.read(data)
        
        return UpdateLangPackTooLong(lang_code=lang_code)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.lang_code))
        
        return data.getvalue()
