from typing import Union
from pyeitaa import raw

DestroyAuthKeyRes = Union[raw.types.DestroyAuthKeyFail, raw.types.DestroyAuthKeyFail, raw.types.DestroyAuthKeyNone, raw.types.DestroyAuthKeyNone, raw.types.DestroyAuthKeyOk, raw.types.DestroyAuthKeyOk]


# noinspection PyRedeclaration
class DestroyAuthKeyRes:
    """This base type has 6 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`DestroyAuthKeyFail <pyeitaa.raw.types.DestroyAuthKeyFail>`
            - :obj:`DestroyAuthKeyFail <pyeitaa.raw.types.DestroyAuthKeyFail>`
            - :obj:`DestroyAuthKeyNone <pyeitaa.raw.types.DestroyAuthKeyNone>`
            - :obj:`DestroyAuthKeyNone <pyeitaa.raw.types.DestroyAuthKeyNone>`
            - :obj:`DestroyAuthKeyOk <pyeitaa.raw.types.DestroyAuthKeyOk>`
            - :obj:`DestroyAuthKeyOk <pyeitaa.raw.types.DestroyAuthKeyOk>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`DestroyAuthKey <pyeitaa.raw.functions.DestroyAuthKey>`
            - :obj:`DestroyAuthKey <pyeitaa.raw.functions.DestroyAuthKey>`
    """

    QUALNAME = "pyeitaa.raw.base.DestroyAuthKeyRes"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
