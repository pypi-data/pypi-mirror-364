from typing import Union
from pyeitaa import raw

User = Union[raw.types.User, raw.types.UserEmpty]


# noinspection PyRedeclaration
class User:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`User <pyeitaa.raw.types.User>`
            - :obj:`UserEmpty <pyeitaa.raw.types.UserEmpty>`

    See Also:
        This object can be returned by 4 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.UpdateProfile <pyeitaa.raw.functions.account.UpdateProfile>`
            - :obj:`account.UpdateUsername <pyeitaa.raw.functions.account.UpdateUsername>`
            - :obj:`account.ChangePhone <pyeitaa.raw.functions.account.ChangePhone>`
            - :obj:`users.GetUsers <pyeitaa.raw.functions.users.GetUsers>`
    """

    QUALNAME = "pyeitaa.raw.base.User"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
