from typing import Union
from pyeitaa import raw

InviteText = Union[raw.types.help.InviteText]


# noinspection PyRedeclaration
class InviteText:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.InviteText <pyeitaa.raw.types.help.InviteText>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetInviteText <pyeitaa.raw.functions.help.GetInviteText>`
    """

    QUALNAME = "pyeitaa.raw.base.help.InviteText"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
