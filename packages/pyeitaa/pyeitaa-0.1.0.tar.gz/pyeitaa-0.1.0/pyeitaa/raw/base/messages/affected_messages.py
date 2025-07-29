from typing import Union
from pyeitaa import raw

AffectedMessages = Union[raw.types.messages.AffectedMessages]


# noinspection PyRedeclaration
class AffectedMessages:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.AffectedMessages <pyeitaa.raw.types.messages.AffectedMessages>`

    See Also:
        This object can be returned by 4 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.ReadHistory <pyeitaa.raw.functions.messages.ReadHistory>`
            - :obj:`messages.DeleteMessages <pyeitaa.raw.functions.messages.DeleteMessages>`
            - :obj:`messages.ReadMessageContents <pyeitaa.raw.functions.messages.ReadMessageContents>`
            - :obj:`channels.DeleteMessages <pyeitaa.raw.functions.channels.DeleteMessages>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.AffectedMessages"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
