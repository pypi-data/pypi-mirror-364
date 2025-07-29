from typing import Union
from pyeitaa import raw

ExportedChatInvite = Union[raw.types.ChatInviteEmptyLayer122, raw.types.ChatInviteExported, raw.types.ChatInviteExportedLayer122]


# noinspection PyRedeclaration
class ExportedChatInvite:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChatInviteEmptyLayer122 <pyeitaa.raw.types.ChatInviteEmptyLayer122>`
            - :obj:`ChatInviteExported <pyeitaa.raw.types.ChatInviteExported>`
            - :obj:`ChatInviteExportedLayer122 <pyeitaa.raw.types.ChatInviteExportedLayer122>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.ExportChatInvite <pyeitaa.raw.functions.messages.ExportChatInvite>`
            - :obj:`messages.ExportChatInviteLayer84 <pyeitaa.raw.functions.messages.ExportChatInviteLayer84>`
    """

    QUALNAME = "pyeitaa.raw.base.ExportedChatInvite"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
