from typing import Union
from pyeitaa import raw

DiscussionMessage = Union[raw.types.messages.DiscussionMessage]


# noinspection PyRedeclaration
class DiscussionMessage:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.DiscussionMessage <pyeitaa.raw.types.messages.DiscussionMessage>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetDiscussionMessage <pyeitaa.raw.functions.messages.GetDiscussionMessage>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.DiscussionMessage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
