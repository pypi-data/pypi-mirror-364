from typing import Union
from pyeitaa import raw

Authorizations = Union[raw.types.account.Authorizations]


# noinspection PyRedeclaration
class Authorizations:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.Authorizations <pyeitaa.raw.types.account.Authorizations>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetAuthorizations <pyeitaa.raw.functions.account.GetAuthorizations>`
    """

    QUALNAME = "pyeitaa.raw.base.account.Authorizations"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
