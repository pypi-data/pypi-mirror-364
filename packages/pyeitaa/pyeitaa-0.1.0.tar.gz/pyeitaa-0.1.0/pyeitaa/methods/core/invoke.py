import logging

import pyeitaa
from ...raw.all import layer
from ...raw.core import TLObject
from ...raw.types.error import Error
from ...raw.types.rpc_error import RpcError
from ...raw.types.eitaa_app_info import EitaaAppInfo
from ...raw.functions.eitaa_object import EitaaObject
from ...raw.functions.eitaa_refresh_token import EitaaRefreshToken
from ...raw.functions.eitaa_token_updating import EitaaTokenUpdating
from ...raw.functions.eitaa_updates_expire_token import EitaaUpdatesExpireToken

from ...session_internals import DcType
from ...errors.rpc_error import RPCError as TLException

log = logging.getLogger(__name__)

error_types = (Error, RpcError)
expired_token_types = (EitaaTokenUpdating, EitaaUpdatesExpireToken)


class Invoke:
    async def invoke(
        self: "pyeitaa.Client",
        query: TLObject,
        dc_type: DcType = DcType.CLIENT,
        check_connection: bool = True
    ):
        if check_connection and not self.is_initialized:
            raise ConnectionError("Client has not been started yet")

        data = EitaaObject(
            token=self.storage.token or "",
            imei=self.storage.imei,
            packed_data=query.write(),
            layer=layer,
            flags=32 if self.lang_code == "fa" else 128
        )

        result = await self.transporter.send(data.write(), dc_type)

        try:
            tlbject = TLObject.read(result)

        except KeyError as err:
            raise KeyError(f"Invalid TL-Object: {hex(err.args[0])}")

        if isinstance(tlbject, expired_token_types):
            eitaa_updates_token = await self.invoke(
                EitaaRefreshToken(
                    app_info=EitaaAppInfo(
                        build_version=1,
                        system_version=self.system_version,
                        device_model=self.device_model,
                        app_version=self.app_version,
                        lang_code=self.lang_code,
                        sign=""
                    )
                ),
                check_connection=check_connection
            )

            self.storage.token = eitaa_updates_token.token

            log.info("Token updated")

            return self.invoke(query, dc_type)

        if isinstance(tlbject, error_types):
            return TLException.raise_it(tlbject, query)

        return tlbject