from typing import Union
from pyeitaa import raw

LiveGetParticipants = Union[raw.types.LiveGetParticipants]


# noinspection PyRedeclaration
class LiveGetParticipants:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`LiveGetParticipants <pyeitaa.raw.types.LiveGetParticipants>`
    """

    QUALNAME = "pyeitaa.raw.base.LiveGetParticipants"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
