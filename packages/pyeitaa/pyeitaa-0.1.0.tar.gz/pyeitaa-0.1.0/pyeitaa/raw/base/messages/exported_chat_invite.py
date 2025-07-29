from typing import Union
from pyeitaa import raw

ExportedChatInvite = Union[raw.types.messages.ExportedChatInvite, raw.types.messages.ExportedChatInviteReplaced]


# noinspection PyRedeclaration
class ExportedChatInvite:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.ExportedChatInvite <pyeitaa.raw.types.messages.ExportedChatInvite>`
            - :obj:`messages.ExportedChatInviteReplaced <pyeitaa.raw.types.messages.ExportedChatInviteReplaced>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetExportedChatInvite <pyeitaa.raw.functions.messages.GetExportedChatInvite>`
            - :obj:`messages.EditExportedChatInvite <pyeitaa.raw.functions.messages.EditExportedChatInvite>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.ExportedChatInvite"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
