from typing import Union
from pyeitaa import raw

EitaaTokenUpdating = Union[raw.types.EitaaTokenUpdating]


# noinspection PyRedeclaration
class EitaaTokenUpdating:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EitaaTokenUpdating <pyeitaa.raw.types.EitaaTokenUpdating>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`EitaaTokenUpdating <pyeitaa.raw.functions.EitaaTokenUpdating>`
    """

    QUALNAME = "pyeitaa.raw.base.EitaaTokenUpdating"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
