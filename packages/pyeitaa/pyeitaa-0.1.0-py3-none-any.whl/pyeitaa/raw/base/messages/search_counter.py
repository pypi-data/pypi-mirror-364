from typing import Union
from pyeitaa import raw

SearchCounter = Union[raw.types.messages.SearchCounter]


# noinspection PyRedeclaration
class SearchCounter:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.SearchCounter <pyeitaa.raw.types.messages.SearchCounter>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetSearchCounters <pyeitaa.raw.functions.messages.GetSearchCounters>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.SearchCounter"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
