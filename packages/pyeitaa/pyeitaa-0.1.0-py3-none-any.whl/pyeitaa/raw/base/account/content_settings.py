from typing import Union
from pyeitaa import raw

ContentSettings = Union[raw.types.account.ContentSettings]


# noinspection PyRedeclaration
class ContentSettings:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.ContentSettings <pyeitaa.raw.types.account.ContentSettings>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetContentSettings <pyeitaa.raw.functions.account.GetContentSettings>`
    """

    QUALNAME = "pyeitaa.raw.base.account.ContentSettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
