from typing import Union
from pyeitaa import raw

AffectedHistory = Union[raw.types.messages.AffectedHistory]


# noinspection PyRedeclaration
class AffectedHistory:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.AffectedHistory <pyeitaa.raw.types.messages.AffectedHistory>`

    See Also:
        This object can be returned by 4 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.DeleteHistory <pyeitaa.raw.functions.messages.DeleteHistory>`
            - :obj:`messages.ReadMentions <pyeitaa.raw.functions.messages.ReadMentions>`
            - :obj:`messages.UnpinAllMessages <pyeitaa.raw.functions.messages.UnpinAllMessages>`
            - :obj:`channels.DeleteUserHistory <pyeitaa.raw.functions.channels.DeleteUserHistory>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.AffectedHistory"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
