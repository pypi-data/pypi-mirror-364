import logging

import pyeitaa

from ...raw.functions.auth import SendCode as SendCode_
from ...raw.types.code_settings import CodeSettings

from ...types.authorization.sent_code import SentCode

log = logging.getLogger(__name__)


class SendCode:
    async def send_code(
        self: "pyeitaa.Client",
        phone_number: str,
        current_number: bool = None,
        allow_flashcall: bool = None,
        allow_app_hash: bool = None
    ) -> SentCode:
        """Send the confirmation code to the given phone number.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            phone_number (``str``):
                Phone number in international format (includes the country prefix).

            current_number (``bool``, *optional*):
                Whether the phone number is the current one.

            allow_flashcall (``bool``, *optional*):
                Whether to allow a flash call.

            allow_app_hash (``bool``, *optional*):
                Whether to allow an app hash.

        Returns:
            :obj:`~pyeitaa.types.SentCode`: On success, an object containing information on the sent confirmation code
            is returned.
        """
        phone_number = phone_number.strip()

        r = await self.invoke(
            SendCode_(
                phone_number=phone_number,
                api_id=self.api_id,
                api_hash=self.api_hash,
                settings=CodeSettings(
                    allow_flashcall=allow_flashcall,
                    current_number=current_number,
                    allow_app_hash=allow_app_hash,
                )
            ),
            check_connection=False
        )

        return SentCode._parse(r)
