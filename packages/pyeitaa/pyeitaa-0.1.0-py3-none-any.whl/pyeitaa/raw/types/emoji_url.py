from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EmojiURL(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EmojiURL`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5a8a8c63``

    Parameters:
        url: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetEmojiURL <pyeitaa.raw.functions.messages.GetEmojiURL>`
    """

    __slots__: List[str] = ["url"]

    ID = -0x5a8a8c63
    QUALNAME = "types.EmojiURL"

    def __init__(self, *, url: str) -> None:
        self.url = url  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        url = String.read(data)
        
        return EmojiURL(url=url)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.url))
        
        return data.getvalue()
