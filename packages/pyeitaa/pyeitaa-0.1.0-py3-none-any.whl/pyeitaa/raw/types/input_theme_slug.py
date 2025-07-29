from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputThemeSlug(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputTheme`.

    Details:
        - Layer: ``135``
        - ID: ``-0xa76f20f``

    Parameters:
        slug: ``str``
    """

    __slots__: List[str] = ["slug"]

    ID = -0xa76f20f
    QUALNAME = "types.InputThemeSlug"

    def __init__(self, *, slug: str) -> None:
        self.slug = slug  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        slug = String.read(data)
        
        return InputThemeSlug(slug=slug)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.slug))
        
        return data.getvalue()
