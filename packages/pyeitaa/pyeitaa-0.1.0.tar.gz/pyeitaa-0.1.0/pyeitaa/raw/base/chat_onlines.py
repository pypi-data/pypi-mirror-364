from typing import Union
from pyeitaa import raw

ChatOnlines = Union[raw.types.ChatOnlines]


# noinspection PyRedeclaration
class ChatOnlines:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChatOnlines <pyeitaa.raw.types.ChatOnlines>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetOnlines <pyeitaa.raw.functions.messages.GetOnlines>`
    """

    QUALNAME = "pyeitaa.raw.base.ChatOnlines"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
