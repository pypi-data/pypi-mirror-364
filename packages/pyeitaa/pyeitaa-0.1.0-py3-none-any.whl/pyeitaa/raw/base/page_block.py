from typing import Union
from pyeitaa import raw

PageBlock = Union[raw.types.PageBlockAnchor, raw.types.PageBlockAudio, raw.types.PageBlockAuthorDate, raw.types.PageBlockBlockquote, raw.types.PageBlockChannel, raw.types.PageBlockCollage, raw.types.PageBlockCover, raw.types.PageBlockDetails, raw.types.PageBlockDivider, raw.types.PageBlockEmbed, raw.types.PageBlockEmbedPost, raw.types.PageBlockFooter, raw.types.PageBlockHeader, raw.types.PageBlockKicker, raw.types.PageBlockList, raw.types.PageBlockMap, raw.types.PageBlockOrderedList, raw.types.PageBlockParagraph, raw.types.PageBlockPhoto, raw.types.PageBlockPreformatted, raw.types.PageBlockPullquote, raw.types.PageBlockRelatedArticles, raw.types.PageBlockSlideshow, raw.types.PageBlockSubheader, raw.types.PageBlockSubtitle, raw.types.PageBlockTable, raw.types.PageBlockTitle, raw.types.PageBlockUnsupported, raw.types.PageBlockVideo]


# noinspection PyRedeclaration
class PageBlock:
    """This base type has 29 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PageBlockAnchor <pyeitaa.raw.types.PageBlockAnchor>`
            - :obj:`PageBlockAudio <pyeitaa.raw.types.PageBlockAudio>`
            - :obj:`PageBlockAuthorDate <pyeitaa.raw.types.PageBlockAuthorDate>`
            - :obj:`PageBlockBlockquote <pyeitaa.raw.types.PageBlockBlockquote>`
            - :obj:`PageBlockChannel <pyeitaa.raw.types.PageBlockChannel>`
            - :obj:`PageBlockCollage <pyeitaa.raw.types.PageBlockCollage>`
            - :obj:`PageBlockCover <pyeitaa.raw.types.PageBlockCover>`
            - :obj:`PageBlockDetails <pyeitaa.raw.types.PageBlockDetails>`
            - :obj:`PageBlockDivider <pyeitaa.raw.types.PageBlockDivider>`
            - :obj:`PageBlockEmbed <pyeitaa.raw.types.PageBlockEmbed>`
            - :obj:`PageBlockEmbedPost <pyeitaa.raw.types.PageBlockEmbedPost>`
            - :obj:`PageBlockFooter <pyeitaa.raw.types.PageBlockFooter>`
            - :obj:`PageBlockHeader <pyeitaa.raw.types.PageBlockHeader>`
            - :obj:`PageBlockKicker <pyeitaa.raw.types.PageBlockKicker>`
            - :obj:`PageBlockList <pyeitaa.raw.types.PageBlockList>`
            - :obj:`PageBlockMap <pyeitaa.raw.types.PageBlockMap>`
            - :obj:`PageBlockOrderedList <pyeitaa.raw.types.PageBlockOrderedList>`
            - :obj:`PageBlockParagraph <pyeitaa.raw.types.PageBlockParagraph>`
            - :obj:`PageBlockPhoto <pyeitaa.raw.types.PageBlockPhoto>`
            - :obj:`PageBlockPreformatted <pyeitaa.raw.types.PageBlockPreformatted>`
            - :obj:`PageBlockPullquote <pyeitaa.raw.types.PageBlockPullquote>`
            - :obj:`PageBlockRelatedArticles <pyeitaa.raw.types.PageBlockRelatedArticles>`
            - :obj:`PageBlockSlideshow <pyeitaa.raw.types.PageBlockSlideshow>`
            - :obj:`PageBlockSubheader <pyeitaa.raw.types.PageBlockSubheader>`
            - :obj:`PageBlockSubtitle <pyeitaa.raw.types.PageBlockSubtitle>`
            - :obj:`PageBlockTable <pyeitaa.raw.types.PageBlockTable>`
            - :obj:`PageBlockTitle <pyeitaa.raw.types.PageBlockTitle>`
            - :obj:`PageBlockUnsupported <pyeitaa.raw.types.PageBlockUnsupported>`
            - :obj:`PageBlockVideo <pyeitaa.raw.types.PageBlockVideo>`
    """

    QUALNAME = "pyeitaa.raw.base.PageBlock"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
