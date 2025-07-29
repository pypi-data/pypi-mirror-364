from typing import Union
from pyeitaa import raw

InputTheme = Union[raw.types.InputTheme, raw.types.InputThemeSlug]


# noinspection PyRedeclaration
class InputTheme:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputTheme <pyeitaa.raw.types.InputTheme>`
            - :obj:`InputThemeSlug <pyeitaa.raw.types.InputThemeSlug>`
    """

    QUALNAME = "pyeitaa.raw.base.InputTheme"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
