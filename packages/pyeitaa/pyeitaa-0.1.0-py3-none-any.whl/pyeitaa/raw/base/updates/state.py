from typing import Union
from pyeitaa import raw

State = Union[raw.types.updates.State]


# noinspection PyRedeclaration
class State:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`updates.State <pyeitaa.raw.types.updates.State>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`updates.GetState <pyeitaa.raw.functions.updates.GetState>`
    """

    QUALNAME = "pyeitaa.raw.base.updates.State"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
