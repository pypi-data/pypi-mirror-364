from typing import Union
from pyeitaa import raw

WebAuthorizations = Union[raw.types.account.WebAuthorizations]


# noinspection PyRedeclaration
class WebAuthorizations:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.WebAuthorizations <pyeitaa.raw.types.account.WebAuthorizations>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetWebAuthorizations <pyeitaa.raw.functions.account.GetWebAuthorizations>`
    """

    QUALNAME = "pyeitaa.raw.base.account.WebAuthorizations"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
