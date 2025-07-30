from . import GoObject
from ... import complexjson
from .go_exception import GoException

"""
{
  "id": "some response identifier",
  "sessionId": "some reusable sessionId if provided on the request",
  "status": 200,
  "target": "the target url",
  "body": "The Response as string here or the error message",
  "headers": {},
  "cookies": {}
}
"""


class Response(GoObject):
    def __init__(
            self,
            id: str,
            session_id: str = "",
            status: int = 0,
            target: str = "",
            body: str = "",
            headers: dict[str, str] = None,
            cookies: dict[str, str] = None,
            used_protocol: str = ""
    ):
        super().__init__(id)
        self.session_id = session_id
        self.status = status
        self.target = target
        self.body = body
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.used_protocol = used_protocol

        self._exception = GoException(self.body) if self.status == 0 else None

    @classmethod
    def from_bytes(cls, byte_string: bytes):
        data = complexjson.loads(byte_string)
        return cls(
            id=data.get("id"),
            session_id=data.get("sessionId", ""),
            status=data.get("status", 0),
            target=data.get("target", ""),
            body=data.get("body", ""),
            headers=data.get("headers"),
            cookies=data.get("cookies"),
            used_protocol=data.get("usedProtocol", "")
        )

    def raise_for_exception(self):
        if self._exception:
            raise self._exception
