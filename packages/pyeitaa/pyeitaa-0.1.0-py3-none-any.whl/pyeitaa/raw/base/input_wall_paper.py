from typing import Union
from pyeitaa import raw

InputWallPaper = Union[raw.types.InputWallPaper, raw.types.InputWallPaperNoFile, raw.types.InputWallPaperSlug]


# noinspection PyRedeclaration
class InputWallPaper:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputWallPaper <pyeitaa.raw.types.InputWallPaper>`
            - :obj:`InputWallPaperNoFile <pyeitaa.raw.types.InputWallPaperNoFile>`
            - :obj:`InputWallPaperSlug <pyeitaa.raw.types.InputWallPaperSlug>`
    """

    QUALNAME = "pyeitaa.raw.base.InputWallPaper"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
