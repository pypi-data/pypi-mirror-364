from typing import Union
from pyeitaa import raw

WallPaperSettings = Union[raw.types.WallPaperSettings]


# noinspection PyRedeclaration
class WallPaperSettings:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`WallPaperSettings <pyeitaa.raw.types.WallPaperSettings>`
    """

    QUALNAME = "pyeitaa.raw.base.WallPaperSettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
