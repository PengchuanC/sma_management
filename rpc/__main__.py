import asyncio
from rpc import server


asyncio.run(server.Server.serve())
