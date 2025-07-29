from typing import Union
from pyeitaa import raw

VotesList = Union[raw.types.messages.VotesList]


# noinspection PyRedeclaration
class VotesList:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.VotesList <pyeitaa.raw.types.messages.VotesList>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetPollVotes <pyeitaa.raw.functions.messages.GetPollVotes>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.VotesList"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
