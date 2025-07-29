from typing import Union
from pyeitaa import raw

ChatThemes = Union[raw.types.account.ChatThemes, raw.types.account.ChatThemesNotModified]


# noinspection PyRedeclaration
class ChatThemes:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.ChatThemes <pyeitaa.raw.types.account.ChatThemes>`
            - :obj:`account.ChatThemesNotModified <pyeitaa.raw.types.account.ChatThemesNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetChatThemes <pyeitaa.raw.functions.account.GetChatThemes>`
    """

    QUALNAME = "pyeitaa.raw.base.account.ChatThemes"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
