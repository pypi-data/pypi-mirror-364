from typing import Union
from pyeitaa import raw

JoinAsPeers = Union[raw.types.phone.JoinAsPeers]


# noinspection PyRedeclaration
class JoinAsPeers:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`phone.JoinAsPeers <pyeitaa.raw.types.phone.JoinAsPeers>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`phone.GetGroupCallJoinAs <pyeitaa.raw.functions.phone.GetGroupCallJoinAs>`
    """

    QUALNAME = "pyeitaa.raw.base.phone.JoinAsPeers"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
