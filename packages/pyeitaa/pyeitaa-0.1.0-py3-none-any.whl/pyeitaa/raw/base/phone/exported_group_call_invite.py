from typing import Union
from pyeitaa import raw

ExportedGroupCallInvite = Union[raw.types.phone.ExportedGroupCallInvite]


# noinspection PyRedeclaration
class ExportedGroupCallInvite:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`phone.ExportedGroupCallInvite <pyeitaa.raw.types.phone.ExportedGroupCallInvite>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`phone.ExportGroupCallInvite <pyeitaa.raw.functions.phone.ExportGroupCallInvite>`
    """

    QUALNAME = "pyeitaa.raw.base.phone.ExportedGroupCallInvite"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
