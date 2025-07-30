from ... import complexjson
from .... import cffi


class GoObject:
    def __init__(self, id: str):
        self.id = id

        self._memory_allocated = True

    def release(self):
        if self._memory_allocated:
            cffi.free_memory(self.id)
            self._memory_allocated = False

    def __del__(self):
        self.release()

    @classmethod
    def from_bytes(cls, byte_string: bytes):
        data = complexjson.loads(byte_string)
        return cls(
            id=data.get("id")
        )
