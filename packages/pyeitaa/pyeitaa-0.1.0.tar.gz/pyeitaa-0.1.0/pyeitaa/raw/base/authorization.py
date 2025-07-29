from typing import Union
from pyeitaa import raw

Authorization = Union[raw.types.Authorization]


# noinspection PyRedeclaration
class Authorization:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Authorization <pyeitaa.raw.types.Authorization>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`auth.AcceptLoginToken <pyeitaa.raw.functions.auth.AcceptLoginToken>`
    """

    QUALNAME = "pyeitaa.raw.base.Authorization"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
