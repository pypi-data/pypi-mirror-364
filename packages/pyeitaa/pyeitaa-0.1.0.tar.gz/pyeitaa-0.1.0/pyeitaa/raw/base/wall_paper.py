from typing import Union
from pyeitaa import raw

WallPaper = Union[raw.types.WallPaper, raw.types.WallPaperNoFile]


# noinspection PyRedeclaration
class WallPaper:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`WallPaper <pyeitaa.raw.types.WallPaper>`
            - :obj:`WallPaperNoFile <pyeitaa.raw.types.WallPaperNoFile>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetWallPaper <pyeitaa.raw.functions.account.GetWallPaper>`
            - :obj:`account.UploadWallPaper <pyeitaa.raw.functions.account.UploadWallPaper>`
            - :obj:`account.GetMultiWallPapers <pyeitaa.raw.functions.account.GetMultiWallPapers>`
    """

    QUALNAME = "pyeitaa.raw.base.WallPaper"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
