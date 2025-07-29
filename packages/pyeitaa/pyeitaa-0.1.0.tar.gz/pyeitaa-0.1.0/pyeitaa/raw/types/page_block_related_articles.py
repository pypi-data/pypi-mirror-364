from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageBlockRelatedArticles(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``0x16115a96``

    Parameters:
        title: :obj:`RichText <pyeitaa.raw.base.RichText>`
        articles: List of :obj:`PageRelatedArticle <pyeitaa.raw.base.PageRelatedArticle>`
    """

    __slots__: List[str] = ["title", "articles"]

    ID = 0x16115a96
    QUALNAME = "types.PageBlockRelatedArticles"

    def __init__(self, *, title: "raw.base.RichText", articles: List["raw.base.PageRelatedArticle"]) -> None:
        self.title = title  # RichText
        self.articles = articles  # Vector<PageRelatedArticle>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        title = TLObject.read(data)
        
        articles = TLObject.read(data)
        
        return PageBlockRelatedArticles(title=title, articles=articles)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.title.write())
        
        data.write(Vector(self.articles))
        
        return data.getvalue()
