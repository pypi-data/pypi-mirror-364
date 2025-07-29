from typing import Union
from pyeitaa import raw

PollAnswer = Union[raw.types.PollAnswer]


# noinspection PyRedeclaration
class PollAnswer:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PollAnswer <pyeitaa.raw.types.PollAnswer>`
    """

    QUALNAME = "pyeitaa.raw.base.PollAnswer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
