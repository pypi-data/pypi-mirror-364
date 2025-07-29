from typing import Union
from pyeitaa import raw

PageRelatedArticle = Union[raw.types.PageRelatedArticle]


# noinspection PyRedeclaration
class PageRelatedArticle:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PageRelatedArticle <pyeitaa.raw.types.PageRelatedArticle>`
    """

    QUALNAME = "pyeitaa.raw.base.PageRelatedArticle"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
