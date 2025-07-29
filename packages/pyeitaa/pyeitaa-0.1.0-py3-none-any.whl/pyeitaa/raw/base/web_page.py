from typing import Union
from pyeitaa import raw

WebPage = Union[raw.types.WebPage, raw.types.WebPageEmpty, raw.types.WebPageNotModified, raw.types.WebPagePending]


# noinspection PyRedeclaration
class WebPage:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`WebPage <pyeitaa.raw.types.WebPage>`
            - :obj:`WebPageEmpty <pyeitaa.raw.types.WebPageEmpty>`
            - :obj:`WebPageNotModified <pyeitaa.raw.types.WebPageNotModified>`
            - :obj:`WebPagePending <pyeitaa.raw.types.WebPagePending>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPage <pyeitaa.raw.functions.messages.GetWebPage>`
    """

    QUALNAME = "pyeitaa.raw.base.WebPage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
