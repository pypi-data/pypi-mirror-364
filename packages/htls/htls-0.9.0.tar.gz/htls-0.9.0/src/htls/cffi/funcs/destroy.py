import asyncio

from .. import complexjson
from ...cffi_loader import destroySession, destroyAll
from ..objects.go import DestroySessionObject


def destroy_session(session_id: str) -> DestroySessionObject:
    payload = {"sessionId": session_id}
    result = destroySession(complexjson.dumps(payload).encode("utf-8"))
    return DestroySessionObject.from_bytes(result)


def destroy_all() -> DestroySessionObject:
    result = destroyAll()
    return DestroySessionObject.from_bytes(result)


async def async_destroy_session(session_id: str) -> DestroySessionObject:
    return await asyncio.get_event_loop().run_in_executor(None, destroy_session, session_id)


async def async_destroy_all() -> DestroySessionObject:
    return await asyncio.get_event_loop().run_in_executor(None, destroy_all)
