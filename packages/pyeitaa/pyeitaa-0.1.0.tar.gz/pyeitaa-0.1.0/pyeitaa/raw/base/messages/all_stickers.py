from typing import Union
from pyeitaa import raw

AllStickers = Union[raw.types.messages.AllStickers, raw.types.messages.AllStickersNotModified]


# noinspection PyRedeclaration
class AllStickers:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.AllStickers <pyeitaa.raw.types.messages.AllStickers>`
            - :obj:`messages.AllStickersNotModified <pyeitaa.raw.types.messages.AllStickersNotModified>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetAllStickers <pyeitaa.raw.functions.messages.GetAllStickers>`
            - :obj:`messages.GetMaskStickers <pyeitaa.raw.functions.messages.GetMaskStickers>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.AllStickers"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
