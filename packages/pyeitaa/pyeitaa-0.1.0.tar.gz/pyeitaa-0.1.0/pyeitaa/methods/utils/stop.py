import logging

import pyeitaa


log = logging.getLogger(__name__)


class Stop:
    async def stop(self: "pyeitaa.Client") -> None:
        if not self.is_initialized:
            return
                
        

        try:
            await self.transporter.close()

        except ConnectionError:
            pass

        self.is_initialized = False