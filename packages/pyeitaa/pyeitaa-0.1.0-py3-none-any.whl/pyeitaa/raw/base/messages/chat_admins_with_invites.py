from typing import Union
from pyeitaa import raw

ChatAdminsWithInvites = Union[raw.types.messages.ChatAdminsWithInvites]


# noinspection PyRedeclaration
class ChatAdminsWithInvites:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.ChatAdminsWithInvites <pyeitaa.raw.types.messages.ChatAdminsWithInvites>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetAdminsWithInvites <pyeitaa.raw.functions.messages.GetAdminsWithInvites>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.ChatAdminsWithInvites"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
