from . import GoObject
from ... import complexjson


class DestroySessionObject(GoObject):
    def __init__(self, id: str, success: bool):
        super().__init__(id)
        self.success = success

    @classmethod
    def from_bytes(cls, byte_string: bytes):
        data = complexjson.loads(byte_string)
        return cls(
            id=data.get("id", ""),
            success=data.get("success", False)
        )
