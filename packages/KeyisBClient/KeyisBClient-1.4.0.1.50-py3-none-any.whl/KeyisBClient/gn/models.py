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
        gn_protocol: Optional[str] = None,
        route: Optional[str] = None
    ):
        self._method = method
        self._url = url
        self._payload = payload
        self._cookies = cookies
        self._gn_protocol = gn_protocol
        self._route = route

        self._url.method = method


    def serialize(self) -> bytes:
        """Сериализует объект GNRequest в байтовый формат."""
        if self._gn_protocol is None:
            self.setGNProtocol()
        
        if self._route is None:
            self.setRoute()

        return msgpack.dumps({
            "method": self._method,
            "url": str(self._url),
            "payload": self._payload,
            "cookies": self._cookies,
            "gn": {
                'protocol': self._gn_protocol,
                'route': self._route
            }
        }, use_bin_type=True)

    @staticmethod
    def deserialize(data: bytes) -> 'GNRequest':
        """Десериализует байтовый формат в объект GNRequest."""
        unpacked = msgpack.loads(data, raw=False)
        _url = Url(unpacked["url"])
        if not _url.method:
            _url.method = unpacked["method"]
        return GNRequest(
            method=unpacked["method"],
            url=_url,
            payload=unpacked.get("payload"),
            cookies=unpacked.get("cookies"),
            gn_protocol=unpacked.get("gn", {}).get("protocol"),
            route=unpacked.get("gn", {}).get("route")
        )
    @property
    def method(self) -> str:
        """
        Метод запроса (GET, POST, PUT, DELETE и т.д.)
        """
        return self._method
    
    def setMethod(self, method: str):
        """
        Устанавливает метод запроса.
        :param method: Метод запроса (GET, POST, PUT, DELETE и т.д.)
        """
        self._method = method
        self._url.method = method
    
    @property
    def url(self) -> Url:
        """
        Возвращает URL запроса.
        """
        return self._url

    def setUrl(self, url: Url):
        """
        Устанавливает URL запроса.
        :param url: URL запроса в виде объекта Url.
        """
        self._url = url

    @property
    def payload(self) -> Optional[dict]:
        """
        Возвращает полезную нагрузку запроса.

        Dict с поддержкой байтов.
        Если полезная нагрузка не установлена, возвращает None.
        """
        return self._payload

    def setPayload(self, payload: dict):
        """
        Устанавливает полезную нагрузку запроса.
        :param payload: Dict с поддержкой байтов.
        """
        self._payload = payload

    @property
    def cookies(self) -> Optional[dict]:
        return self._cookies

    def setCookies(self, cookies: dict):
        self._cookies = cookies

    @property
    def gn_protocol(self) -> Optional[str]:
        """
        Возвращает GN протокол

        GN протокол используется для подключения к сети GN.
        Если протокол не установлен, возвращает None.
        """
        return self._gn_protocol
    
    def setGNProtocol(self, gn_protocol: Optional[str] = None):
        """
        Устанавливает GN протокол.
        :param gn_protocol: GN протокол (например, 'gn:tcp:0.1', 'gn:quic',..).
        Если не указан, используется 'gn:quic'.
        """
        if gn_protocol is None:
            gn_protocol = 'gn:quic'
        self._gn_protocol = gn_protocol

    @property
    def route(self) -> Optional[str]:
        """
        Возвращает маршрут запроса.
        Маршрут используется для определения конечной точки запроса в сети GN.
        Если маршрут не установлен, возвращает None.
        """
        return self._route
    
    def setRoute(self, route: Optional[str] = None):
        """
        Устанавливает маршрут запроса.
        :param route: Маршрут запроса (например, 'gn:proxy:request-to-real-server').
        Если не указан, используется 'gn:proxy:request-to-real-server'.
        """
        if route is None:
            route = 'gn:proxy:request-to-real-server'
        self._route = route


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