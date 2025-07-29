from typing import Union
from pyeitaa import raw

TmpPassword = Union[raw.types.account.TmpPassword]


# noinspection PyRedeclaration
class TmpPassword:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.TmpPassword <pyeitaa.raw.types.account.TmpPassword>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetTmpPassword <pyeitaa.raw.functions.account.GetTmpPassword>`
    """

    QUALNAME = "pyeitaa.raw.base.account.TmpPassword"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
