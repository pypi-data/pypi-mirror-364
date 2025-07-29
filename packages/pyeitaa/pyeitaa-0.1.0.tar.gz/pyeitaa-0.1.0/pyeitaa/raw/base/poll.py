from typing import Union
from pyeitaa import raw

Poll = Union[raw.types.Poll]


# noinspection PyRedeclaration
class Poll:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Poll <pyeitaa.raw.types.Poll>`
    """

    QUALNAME = "pyeitaa.raw.base.Poll"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
