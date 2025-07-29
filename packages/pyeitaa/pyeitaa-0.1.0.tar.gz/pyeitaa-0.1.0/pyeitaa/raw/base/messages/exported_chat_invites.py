from typing import Union
from pyeitaa import raw

ExportedChatInvites = Union[raw.types.messages.ExportedChatInvites]


# noinspection PyRedeclaration
class ExportedChatInvites:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.ExportedChatInvites <pyeitaa.raw.types.messages.ExportedChatInvites>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetExportedChatInvites <pyeitaa.raw.functions.messages.GetExportedChatInvites>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.ExportedChatInvites"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
