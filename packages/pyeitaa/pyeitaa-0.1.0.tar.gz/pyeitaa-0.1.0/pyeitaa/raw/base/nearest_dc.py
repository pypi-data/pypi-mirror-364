from typing import Union
from pyeitaa import raw

NearestDc = Union[raw.types.NearestDc]


# noinspection PyRedeclaration
class NearestDc:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`NearestDc <pyeitaa.raw.types.NearestDc>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetNearestDc <pyeitaa.raw.functions.help.GetNearestDc>`
    """

    QUALNAME = "pyeitaa.raw.base.NearestDc"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
