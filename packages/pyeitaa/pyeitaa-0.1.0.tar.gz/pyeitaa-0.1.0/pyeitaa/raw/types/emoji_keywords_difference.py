from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EmojiKeywordsDifference(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EmojiKeywordsDifference`.

    Details:
        - Layer: ``135``
        - ID: ``0x5cc761bd``

    Parameters:
        lang_code: ``str``
        from_version: ``int`` ``32-bit``
        version: ``int`` ``32-bit``
        keywords: List of :obj:`EmojiKeyword <pyeitaa.raw.base.EmojiKeyword>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetEmojiKeywords <pyeitaa.raw.functions.messages.GetEmojiKeywords>`
            - :obj:`messages.GetEmojiKeywordsDifference <pyeitaa.raw.functions.messages.GetEmojiKeywordsDifference>`
    """

    __slots__: List[str] = ["lang_code", "from_version", "version", "keywords"]

    ID = 0x5cc761bd
    QUALNAME = "types.EmojiKeywordsDifference"

    def __init__(self, *, lang_code: str, from_version: int, version: int, keywords: List["raw.base.EmojiKeyword"]) -> None:
        self.lang_code = lang_code  # string
        self.from_version = from_version  # int
        self.version = version  # int
        self.keywords = keywords  # Vector<EmojiKeyword>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        lang_code = String.read(data)
        
        from_version = Int.read(data)
        
        version = Int.read(data)
        
        keywords = TLObject.read(data)
        
        return EmojiKeywordsDifference(lang_code=lang_code, from_version=from_version, version=version, keywords=keywords)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.lang_code))
        
        data.write(Int(self.from_version))
        
        data.write(Int(self.version))
        
        data.write(Vector(self.keywords))
        
        return data.getvalue()
