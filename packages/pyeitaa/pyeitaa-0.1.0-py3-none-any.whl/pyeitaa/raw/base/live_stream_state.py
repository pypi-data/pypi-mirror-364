from typing import Union
from pyeitaa import raw

LiveStreamState = Union[raw.types.LiveStreamStateBroadcasting, raw.types.LiveStreamStateEnded, raw.types.LiveStreamStateEnded2, raw.types.LiveStreamStateInit]


# noinspection PyRedeclaration
class LiveStreamState:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`LiveStreamStateBroadcasting <pyeitaa.raw.types.LiveStreamStateBroadcasting>`
            - :obj:`LiveStreamStateEnded <pyeitaa.raw.types.LiveStreamStateEnded>`
            - :obj:`LiveStreamStateEnded2 <pyeitaa.raw.types.LiveStreamStateEnded2>`
            - :obj:`LiveStreamStateInit <pyeitaa.raw.types.LiveStreamStateInit>`
    """

    QUALNAME = "pyeitaa.raw.base.LiveStreamState"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
