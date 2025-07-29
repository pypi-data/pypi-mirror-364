from typing import Union
from pyeitaa import raw

GroupParticipants = Union[raw.types.phone.GroupParticipants]


# noinspection PyRedeclaration
class GroupParticipants:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`phone.GroupParticipants <pyeitaa.raw.types.phone.GroupParticipants>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`phone.GetGroupParticipants <pyeitaa.raw.functions.phone.GetGroupParticipants>`
    """

    QUALNAME = "pyeitaa.raw.base.phone.GroupParticipants"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
