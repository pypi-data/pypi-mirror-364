from typing import Union
from pyeitaa import raw

LiveParticipants = Union[raw.types.LiveParticipants]


# noinspection PyRedeclaration
class LiveParticipants:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`LiveParticipants <pyeitaa.raw.types.LiveParticipants>`
    """

    QUALNAME = "pyeitaa.raw.base.LiveParticipants"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
