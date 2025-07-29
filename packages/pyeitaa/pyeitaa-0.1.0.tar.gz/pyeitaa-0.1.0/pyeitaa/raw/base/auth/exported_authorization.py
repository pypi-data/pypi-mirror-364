from typing import Union
from pyeitaa import raw

ExportedAuthorization = Union[raw.types.auth.ExportedAuthorization]


# noinspection PyRedeclaration
class ExportedAuthorization:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`auth.ExportedAuthorization <pyeitaa.raw.types.auth.ExportedAuthorization>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`auth.ExportAuthorization <pyeitaa.raw.functions.auth.ExportAuthorization>`
    """

    QUALNAME = "pyeitaa.raw.base.auth.ExportedAuthorization"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
