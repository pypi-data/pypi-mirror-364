from typing import Union
from pyeitaa import raw

RestrictionReason = Union[raw.types.RestrictionReason]


# noinspection PyRedeclaration
class RestrictionReason:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`RestrictionReason <pyeitaa.raw.types.RestrictionReason>`
    """

    QUALNAME = "pyeitaa.raw.base.RestrictionReason"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
