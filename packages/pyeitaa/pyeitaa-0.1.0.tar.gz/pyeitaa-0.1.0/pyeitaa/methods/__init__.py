from .core import Core
from .auth import Auth
from .utils import Utils
from .users import Users


class Methods(
    Core,
    Auth,
    Utils,
    Users,
):
    pass