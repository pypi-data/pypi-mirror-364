from typing import Union
from pyeitaa import raw

GroupCallParticipantVideoSourceGroup = Union[raw.types.GroupCallParticipantVideoSourceGroup]


# noinspection PyRedeclaration
class GroupCallParticipantVideoSourceGroup:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`GroupCallParticipantVideoSourceGroup <pyeitaa.raw.types.GroupCallParticipantVideoSourceGroup>`
    """

    QUALNAME = "pyeitaa.raw.base.GroupCallParticipantVideoSourceGroup"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
