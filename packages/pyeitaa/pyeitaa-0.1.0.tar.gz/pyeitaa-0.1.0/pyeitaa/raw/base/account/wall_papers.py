from typing import Union
from pyeitaa import raw

WallPapers = Union[raw.types.account.WallPapers, raw.types.account.WallPapersNotModified]


# noinspection PyRedeclaration
class WallPapers:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.WallPapers <pyeitaa.raw.types.account.WallPapers>`
            - :obj:`account.WallPapersNotModified <pyeitaa.raw.types.account.WallPapersNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetWallPapers <pyeitaa.raw.functions.account.GetWallPapers>`
    """

    QUALNAME = "pyeitaa.raw.base.account.WallPapers"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
