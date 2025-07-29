from typing import Union
from pyeitaa import raw

SuggestedShortName = Union[raw.types.stickers.SuggestedShortName]


# noinspection PyRedeclaration
class SuggestedShortName:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`stickers.SuggestedShortName <pyeitaa.raw.types.stickers.SuggestedShortName>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`stickers.SuggestShortName <pyeitaa.raw.functions.stickers.SuggestShortName>`
    """

    QUALNAME = "pyeitaa.raw.base.stickers.SuggestedShortName"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
