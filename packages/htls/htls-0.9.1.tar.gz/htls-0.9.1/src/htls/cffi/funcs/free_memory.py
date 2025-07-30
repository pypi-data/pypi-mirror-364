import asyncio

from ...cffi_loader import freeMemory


def free_memory(id: str) -> None:
    freeMemory(id.encode("utf-8"))


async def async_free_memory(id: str) -> None:
    return await asyncio.get_event_loop().run_in_executor(None, free_memory, id)
