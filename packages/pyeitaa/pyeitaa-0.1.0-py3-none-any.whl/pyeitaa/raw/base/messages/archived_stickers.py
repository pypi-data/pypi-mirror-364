from typing import Union
from pyeitaa import raw

ArchivedStickers = Union[raw.types.messages.ArchivedStickers]


# noinspection PyRedeclaration
class ArchivedStickers:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.ArchivedStickers <pyeitaa.raw.types.messages.ArchivedStickers>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetArchivedStickers <pyeitaa.raw.functions.messages.GetArchivedStickers>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.ArchivedStickers"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
