from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputWallPaperSlug(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputWallPaper`.

    Details:
        - Layer: ``135``
        - ID: ``0x72091c80``

    Parameters:
        slug: ``str``
    """

    __slots__: List[str] = ["slug"]

    ID = 0x72091c80
    QUALNAME = "types.InputWallPaperSlug"

    def __init__(self, *, slug: str) -> None:
        self.slug = slug  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        slug = String.read(data)
        
        return InputWallPaperSlug(slug=slug)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.slug))
        
        return data.getvalue()
