from typing import Union
from pyeitaa import raw

FavedStickers = Union[raw.types.messages.FavedStickers, raw.types.messages.FavedStickersNotModified]


# noinspection PyRedeclaration
class FavedStickers:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.FavedStickers <pyeitaa.raw.types.messages.FavedStickers>`
            - :obj:`messages.FavedStickersNotModified <pyeitaa.raw.types.messages.FavedStickersNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetFavedStickers <pyeitaa.raw.functions.messages.GetFavedStickers>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.FavedStickers"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
