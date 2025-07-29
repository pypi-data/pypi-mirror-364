from typing import Union
from pyeitaa import raw

SavedGifs = Union[raw.types.messages.SavedGifs, raw.types.messages.SavedGifsNotModified]


# noinspection PyRedeclaration
class SavedGifs:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.SavedGifs <pyeitaa.raw.types.messages.SavedGifs>`
            - :obj:`messages.SavedGifsNotModified <pyeitaa.raw.types.messages.SavedGifsNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetSavedGifs <pyeitaa.raw.functions.messages.GetSavedGifs>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.SavedGifs"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
