from typing import Union
from pyeitaa import raw

EitaaUpdatesExpireToken = Union[raw.types.EitaaUpdatesExpireToken]


# noinspection PyRedeclaration
class EitaaUpdatesExpireToken:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EitaaUpdatesExpireToken <pyeitaa.raw.types.EitaaUpdatesExpireToken>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`EitaaUpdatesExpireToken <pyeitaa.raw.functions.EitaaUpdatesExpireToken>`
    """

    QUALNAME = "pyeitaa.raw.base.EitaaUpdatesExpireToken"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
