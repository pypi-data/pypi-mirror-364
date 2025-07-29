from typing import Union
from pyeitaa import raw

KeyboardButton = Union[raw.types.InputKeyboardButtonUrlAuth, raw.types.KeyboardButton, raw.types.KeyboardButtonBuy, raw.types.KeyboardButtonCallback, raw.types.KeyboardButtonGame, raw.types.KeyboardButtonRequestGeoLocation, raw.types.KeyboardButtonRequestPhone, raw.types.KeyboardButtonRequestPoll, raw.types.KeyboardButtonSwitchInline, raw.types.KeyboardButtonUrl, raw.types.KeyboardButtonUrlAuth]


# noinspection PyRedeclaration
class KeyboardButton:
    """This base type has 11 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputKeyboardButtonUrlAuth <pyeitaa.raw.types.InputKeyboardButtonUrlAuth>`
            - :obj:`KeyboardButton <pyeitaa.raw.types.KeyboardButton>`
            - :obj:`KeyboardButtonBuy <pyeitaa.raw.types.KeyboardButtonBuy>`
            - :obj:`KeyboardButtonCallback <pyeitaa.raw.types.KeyboardButtonCallback>`
            - :obj:`KeyboardButtonGame <pyeitaa.raw.types.KeyboardButtonGame>`
            - :obj:`KeyboardButtonRequestGeoLocation <pyeitaa.raw.types.KeyboardButtonRequestGeoLocation>`
            - :obj:`KeyboardButtonRequestPhone <pyeitaa.raw.types.KeyboardButtonRequestPhone>`
            - :obj:`KeyboardButtonRequestPoll <pyeitaa.raw.types.KeyboardButtonRequestPoll>`
            - :obj:`KeyboardButtonSwitchInline <pyeitaa.raw.types.KeyboardButtonSwitchInline>`
            - :obj:`KeyboardButtonUrl <pyeitaa.raw.types.KeyboardButtonUrl>`
            - :obj:`KeyboardButtonUrlAuth <pyeitaa.raw.types.KeyboardButtonUrlAuth>`
    """

    QUALNAME = "pyeitaa.raw.base.KeyboardButton"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
