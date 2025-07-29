from typing import Self
from ..object import Object
from ...enums import SentCodeType, NextCodeType
from ...raw.types.auth import SentCode


class SentCode(Object):
    """Contains info on a sent confirmation code.

    Parameters:
        type (:obj:`~pyeitaa.enums.SentCodeType`):
            Type of the current sent code.

        phone_code_hash (``str``):
            Confirmation code identifier useful for the next authorization steps (either
            :meth:`~pyeitaa.Client.sign_in` or :meth:`~pyeitaa.Client.sign_up`).

        next_type (:obj:`~pyeitaa.enums.NextCodeType`, *optional*):
            Type of the next code to be sent with :meth:`~pyeitaa.Client.resend_code`.

        timeout (``int``, *optional*):
            Delay in seconds before calling :meth:`~pyeitaa.Client.resend_code`.
    """

    def __init__(
        self, *,
        type: SentCodeType,
        phone_code_hash: str,
        next_type: NextCodeType = None,
        timeout: int = None
    ):
        super().__init__()

        self.type = type
        self.phone_code_hash = phone_code_hash
        self.next_type = next_type
        self.timeout = timeout

    @staticmethod
    def _parse(sent_code: SentCode) -> Self:
        return SentCode(
            type=SentCodeType(type(sent_code.type)),
            phone_code_hash=sent_code.phone_code_hash,
            next_type=NextCodeType(type(sent_code.next_type)) if sent_code.next_type else None,
            timeout=sent_code.timeout
        )