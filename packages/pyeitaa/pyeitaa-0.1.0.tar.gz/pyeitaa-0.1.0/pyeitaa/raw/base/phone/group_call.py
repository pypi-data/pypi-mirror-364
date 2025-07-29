from typing import Union
from pyeitaa import raw

GroupCall = Union[raw.types.phone.GroupCall]


# noinspection PyRedeclaration
class GroupCall:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`phone.GroupCall <pyeitaa.raw.types.phone.GroupCall>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`phone.GetGroupCall <pyeitaa.raw.functions.phone.GetGroupCall>`
    """

    QUALNAME = "pyeitaa.raw.base.phone.GroupCall"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
