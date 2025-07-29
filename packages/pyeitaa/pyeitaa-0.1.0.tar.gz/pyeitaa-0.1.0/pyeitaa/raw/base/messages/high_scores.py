from typing import Union
from pyeitaa import raw

HighScores = Union[raw.types.messages.HighScores]


# noinspection PyRedeclaration
class HighScores:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.HighScores <pyeitaa.raw.types.messages.HighScores>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetGameHighScores <pyeitaa.raw.functions.messages.GetGameHighScores>`
            - :obj:`messages.GetInlineGameHighScores <pyeitaa.raw.functions.messages.GetInlineGameHighScores>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.HighScores"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
