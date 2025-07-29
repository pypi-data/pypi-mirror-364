from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageMediaWebPage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5cd22a00``

    Parameters:
        webpage: :obj:`WebPage <pyeitaa.raw.base.WebPage>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyeitaa.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyeitaa.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyeitaa.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["webpage"]

    ID = -0x5cd22a00
    QUALNAME = "types.MessageMediaWebPage"

    def __init__(self, *, webpage: "raw.base.WebPage") -> None:
        self.webpage = webpage  # WebPage

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        webpage = TLObject.read(data)
        
        return MessageMediaWebPage(webpage=webpage)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.webpage.write())
        
        return data.getvalue()
