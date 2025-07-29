#!/usr/bin/env python3
#
# Sq1090 Console - show aircraft information
#
# Copyright (C) 2025 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import importlib.resources
import rbfly.streams as rbs
import logging
import os
import time
from blacksheep import Application, Request, get
from blacksheep.server.process import is_stopping
from blacksheep.server.sse import ServerSentEvent
from collections.abc import AsyncIterable

logger = logging.getLogger('sq1090-console')
logging.basicConfig(level=logging.INFO)

async def setup(app: Application) -> AsyncIterable[None]:
    """
    Setup Sq1090 console services.
    """
    with importlib.resources.path('sq1090console', 'web') as rpath:
        app.serve_files(rpath)
        client = rbs.streams_client(os.environ['SQ1090_CONNECTION'])
        app.services.register(rbs.StreamsClient, instance=client)
        try:
            yield
        finally:
            await client.disconnect()
            logger.info('shutdown done')

@get('/aircraft')
async def aircraft_data(
        request: Request,
        client: rbs.StreamsClient,
) -> AsyncIterable[ServerSentEvent]:
    """
    Serve aircraft data as server-sent events (SSE).

    param request: Application request.
    param client: RabbitMQ Streams client.
    """
    offset = rbs.Offset.timestamp(time.time() - 15 * 60)
    async for msg in client.subscribe('sq1090.assembled', offset=offset):
        data = msg[0], msg[1], msg[2][2], *msg[3]  # type: ignore[index,misc]
        yield ServerSentEvent(data)
        if is_stopping() or await request.is_disconnected():
            break

app = Application()
app.lifespan(setup)  # type: ignore[no-untyped-call]

# vim: sw=4:et:ai
