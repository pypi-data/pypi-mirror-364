import msgpack
from typing import Optional
from ..models import Url


class GNRequest:
    def __init__(
        self,
        method: str,
        url: Url,
        payload: Optional[dict] = None, # msqpack object
        cookies: Optional[dict] = None, # передаются один раз. сохраняются на сервере в сессии,
        gn_protocol: Optional[str] = None
    ):
        self._method = method
        self._url = url
        self._payload = payload
        self._cookies = cookies
        self._gn_protocol = gn_protocol

        self._url.method = method


    def serialize(self) -> bytes:
        if self._gn_protocol is None:
            self.setGNProtocol()

        return msgpack.dumps({
            "method": self._method,
            "url": str(self._url),
            "payload": self._payload,
            "cookies": self._cookies,
            "gn": {
                'protocol': self._gn_protocol,
            }
        }, use_bin_type=True)

    @staticmethod
    def deserialize(data: bytes) -> 'GNRequest':
        unpacked = msgpack.loads(data, raw=False)
        _url = Url(unpacked["url"])
        if not _url.method:
            _url.method = unpacked["method"]
        return GNRequest(
            method=unpacked["method"],
            url=_url,
            payload=unpacked.get("payload"),
            cookies=unpacked.get("cookies"),
            gn_protocol=unpacked.get("gn", {}).get("protocol")
        )
    @property
    def method(self) -> str:
        return self._method
    
    def setMethod(self, method: str):
        self._method = method
        self._url.method = method
    
    @property
    def url(self) -> Url:
        return self._url

    def setUrl(self, url: Url):
        self._url = url

    @property
    def payload(self) -> Optional[dict]:
        return self._payload

    def setPayload(self, payload: dict):
        self._payload = payload

    @property
    def cookies(self) -> Optional[dict]:
        return self._cookies

    def setCookies(self, cookies: dict):
        self._cookies = cookies

    @property
    def gn_protocol(self) -> Optional[str]:
        return self._gn_protocol
    
    def setGNProtocol(self, gn_protocol: Optional[str] = None):
        if gn_protocol is None:
            gn_protocol = 'gn:quic'
        self._gn_protocol = gn_protocol

    def __repr__(self):
        return f"<GNRequest [{self._method} {self._url}]>"
    
class GNResponse:
    def __init__(self, command: str, payload: Optional[bytes]):
        self._command = command
        self._payload = payload
    def serialize(self) -> bytes:
        return msgpack.dumps({
            "command": self._command,
            "payload": self._payload
        }, use_bin_type=True)
    
    @staticmethod
    def deserialize(payload: bytes) -> 'GNResponse':
        unpacked = msgpack.loads(payload, raw=False)
        return GNResponse(
            command=unpacked.get("command", 'gn/not_command'),
            payload=unpacked.get("payload")
        )

    def command(self) -> str:
        return self._command

    def payload(self) -> Optional[dict]:
        return self._payload