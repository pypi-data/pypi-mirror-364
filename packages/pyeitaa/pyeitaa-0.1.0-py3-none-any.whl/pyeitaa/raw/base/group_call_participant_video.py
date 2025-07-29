from typing import Union
from pyeitaa import raw

GroupCallParticipantVideo = Union[raw.types.GroupCallParticipantVideo]


# noinspection PyRedeclaration
class GroupCallParticipantVideo:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`GroupCallParticipantVideo <pyeitaa.raw.types.GroupCallParticipantVideo>`
    """

    QUALNAME = "pyeitaa.raw.base.GroupCallParticipantVideo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
