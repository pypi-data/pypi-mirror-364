from typing import Union
from pyeitaa import raw

MessageUserVote = Union[raw.types.MessageUserVote, raw.types.MessageUserVoteInputOption, raw.types.MessageUserVoteMultiple]


# noinspection PyRedeclaration
class MessageUserVote:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MessageUserVote <pyeitaa.raw.types.MessageUserVote>`
            - :obj:`MessageUserVoteInputOption <pyeitaa.raw.types.MessageUserVoteInputOption>`
            - :obj:`MessageUserVoteMultiple <pyeitaa.raw.types.MessageUserVoteMultiple>`
    """

    QUALNAME = "pyeitaa.raw.base.MessageUserVote"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
