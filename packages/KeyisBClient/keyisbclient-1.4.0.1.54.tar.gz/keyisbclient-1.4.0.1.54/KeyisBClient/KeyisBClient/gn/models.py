from __future__ import annotations
import msgpack
from typing import Optional
import re
from functools import lru_cache
from typing import Iterable, List, NamedTuple, Optional, Tuple, Union
from ..models import Url
import asyncio


class GNRequest:
    def __init__(
        self,
        method: str,
        url: Url,
        payload: Optional[dict] = None, # msqpack object
        cookies: Optional[dict] = None, # передаются один раз. сохраняются на сервере в сессии,
        gn_protocol: Optional[str] = None,
        route: Optional[str] = None,
        stream: bool = False
    ):
        self._method = method
        self._url = url
        self._payload = payload
        self._cookies = cookies
        self._gn_protocol = gn_protocol
        self._route = route
        self._stream = stream

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
            "stream": self._stream,
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
            stream=unpacked.get("stream"),
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
    def gn_protocol(self) -> Optional['GNProtocol']:
        """
        Возвращает GN протокол

        GN протокол используется для подключения к сети GN.
        Если протокол не установлен, возвращает None.
        """
        return GNProtocol(self._gn_protocol) if self._gn_protocol else None

    @property
    def gn_protocol_str(self) -> Optional[str]:
        """
        Возвращает GN протокол в виде строки.
        Если GN протокол не установлен, возвращает None.
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
    def __init__(self, command: str, payload: Optional[dict] = None):
        self._command = command
        self._payload = payload
        self._stream: asyncio.Queue | None = None
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
    





# ───────────────── helpers ────────────────────────────────────────────────────

# ────────────────── fast helpers ──────────────────────────────────────────────
_VERSION_RE = re.compile(r"^\d+(?:\.\d+)*(?:-\d+(?:\.\d+)*)?$").match  # >30% быстрее
_is_ver = _VERSION_RE  # micro‑alias


def _to_list(v: str) -> List[int]:
    return [int(x) for x in v.split(".")] if v else []


def _cmp(a: List[int], b: List[int]) -> int:
    n = max(len(a), len(b))
    a += [0] * (n - len(a))
    b += [0] * (n - len(b))
    return (a > b) - (a < b)


# ────────────────── VersionRange ──────────────────────────────────────────────
class _VersionRange:
    """Одиночная версия, диапазон a‑b, 'last' или wildcard (None)."""

    __slots__ = ("raw", "kind", "lo", "hi", "single")

    def __init__(self, raw: Optional[str]):
        self.raw = raw             # None == wildcard
        if raw is None:
            self.kind = "wild"
            return
        if raw.lower() == "last":
            self.kind = "single_last"
            return
        if "-" in raw:
            self.kind = "range"
            lo, hi = raw.split("-", 1)
            self.lo = _to_list(lo)
            self.hi = _to_list(hi)
        else:
            self.kind = "single"
            self.single = _to_list(raw)

    def contains(self, ver: Optional[str]) -> bool:  # noqa: C901
        if self.kind == "wild":
            return True
        ver = ver or "last"
        if self.kind == "single_last":
            return ver.lower() == "last"
        if ver.lower() == "last":
            return False
        v = _to_list(ver)
        if self.kind == "single":
            return _cmp(self.single[:], v) == 0
        return _cmp(self.lo[:], v) <= 0 <= _cmp(v, self.hi[:])

    # for debugging / logs
    def __str__(self) -> str:
        return self.raw or "last"


# ────────────────── fast pattern caches ───────────────────────────────────────
class _Pat(NamedTuple):
    gn_ver: _VersionRange
    p1_name: Optional[str]
    p1_ver: _VersionRange
    p1_need_last: bool
    p2_name: Optional[str]
    p2_ver: _VersionRange
    p2_need_last: bool


@lru_cache(maxsize=2048)
def _compile_full_pattern(pat: str) -> _Pat:
    # full three‑level pattern (used rarely ⇒ modest optimisation)
    t = pat.split(":")
    gn_ver = _VersionRange(None)
    if t and t[0].lower() == "gn":
        t.pop(0)
        gn_ver = _VersionRange(t.pop(0)) if t and (_is_ver(t[0]) or t[0].lower() == "last") else _VersionRange(None)

    p2_name = p2_ver = p1_name = p1_ver = None
    p2_need_last = p1_need_last = False

    if t:
        if _is_ver(t[-1]) or t[-1].lower() == "last":
            p2_ver = _VersionRange(t.pop())
        else:
            p2_need_last = True
        p2_name = t.pop() if t else None

    if t:
        if _is_ver(t[-1]) or t[-1].lower() == "last":
            p1_ver = _VersionRange(t.pop())
        else:
            p1_need_last = True
        p1_name = t.pop() if t else None

    if t:
        raise ValueError(f"bad pattern {pat!r}")

    return _Pat(
        gn_ver=gn_ver,
        p1_name=None if p1_name is None else p1_name.lower(),
        p1_ver=p1_ver or _VersionRange(None),
        p1_need_last=p1_need_last,
        p2_name=None if p2_name is None else p2_name.lower(),
        p2_ver=p2_ver or _VersionRange(None),
        p2_need_last=p2_need_last,
    )


class _LeafPat(NamedTuple):
    name: Optional[str]           # None → имя игнорируется
    ver: _VersionRange
    need_last: bool               # версия не указана → требуем last


@lru_cache(maxsize=4096)
def _compile_leaf_pattern(pat: str) -> _LeafPat:
    """
    pattern ::= NAME
              | NAME ':' VERSION
              | VERSION             (# имя опущено)
    """
    if ":" not in pat:
        if _is_ver(pat) or pat.lower() == "last":
            return _LeafPat(name=None, ver=_VersionRange(pat), need_last=False)
        # только имя → версия «должна быть last»
        return _LeafPat(name=pat.lower(), ver=_VersionRange(None), need_last=True)

    name, ver = pat.split(":", 1)
    name = name.lower() or None
    need_last = False
    if not ver:                   # ':' без версии  → last
        need_last = True
        ver_range = _VersionRange(None)
    else:
        ver_range = _VersionRange(ver)
    return _LeafPat(name=name, ver=ver_range, need_last=need_last)


# ────────────────── main class ────────────────────────────────────────────────
class GNProtocol:
    """
    Строка формата  gn[:gnVer]:connection[:ver1]:route[:ver2]
    """

    __slots__ = (
        "raw",
        "gn_ver_raw",
        "gn_ver",
        "conn_name",
        "conn_ver_raw",
        "conn_ver",
        "route_name",
        "route_ver_raw",
        "route_ver",
        "_gn_leaf",
        "_conn_leaf",
        "_route_leaf",
    )

    # ---------------------------------------------------------------- init ---
    def __init__(self, raw: str):
        self.raw = raw
        self._parse()
        # pre‑create leaf objects (будут дергаться чаще всего)
        self._gn_leaf = self._LeafProto("gn", self.gn_ver_raw)
        self._conn_leaf = self._LeafProto(self.conn_name, self.conn_ver_raw)
        self._route_leaf = self._LeafProto(self.route_name, self.route_ver_raw)

    # ---------------------------------------------------------------- parse --
    @staticmethod
    def _take_ver(tokens: List[str]) -> Optional[str]:
        return tokens.pop(0) if tokens and (_is_ver(tokens[0]) or tokens[0].lower() == "last") else None

    def _parse(self) -> None:
        t = self.raw.split(":")
        if not t or t[0].lower() != "gn":
            raise ValueError("must start with 'gn'")
        t.pop(0)

        self.gn_ver_raw = self._take_ver(t)
        self.gn_ver = _VersionRange(self.gn_ver_raw)

        if not t:
            raise ValueError("missing connection proto")
        self.conn_name = t.pop(0).lower()
        self.conn_ver_raw = self._take_ver(t)
        self.conn_ver = _VersionRange(self.conn_ver_raw)

        if not t:
            raise ValueError("missing route proto")
        self.route_name = t.pop(0).lower()
        self.route_ver_raw = self._take_ver(t)
        self.route_ver = _VersionRange(self.route_ver_raw)

        if t:
            raise ValueError(f"extra tokens: {t!r}")

    # ────────────────── public (rarely called) ───────────────────────────────
    def structure(self) -> dict:
        return {
            "gn": {"version": str(self.gn_ver)},
            self.conn_name: {"version": str(self.conn_ver)},
            self.route_name: {"version": str(self.route_ver)},
        }

    def matches_any(self, patterns: Iterable[str]) -> bool:
        """Полное трёхуровневое сравнение (используется сравнительно редко)."""
        gv = self.gn_ver_raw
        c_name, c_ver = self.conn_name, self.conn_ver_raw
        r_name, r_ver = self.route_name, self.route_ver_raw

        for pat in patterns:
            gn_v, p1n, p1v, p1need, p2n, p2v, p2need = _compile_full_pattern(pat)

            # gn
            if not gn_v.contains(gv):
                continue

            # connection
            if p1n and p1n != c_name:
                continue
            if p1need:
                if c_ver is not None:
                    continue
            elif not p1v.contains(c_ver):
                continue

            # route
            if p2n and p2n != r_name:
                continue
            if p2need:
                if r_ver is not None:
                    continue
            elif not p2v.contains(r_ver):
                continue

            return True
        return False

    # ────────────────── ultra‑hot leaf objects ────────────────────────────────
    class _LeafProto:
        __slots__ = ("_name", "_ver_raw")

        def __init__(self, name: str, ver_raw: Optional[str]):
            self._name = name
            self._ver_raw = ver_raw  # None == 'last'

        # ───────── getters ──────────────────────────────────────────────
        def protocol(self) -> str:                    # 'proton'
            return self._name

        def version(self) -> str:                     # 'last' / '1.2'
            return self._ver_raw or "last"

        # ───────── hot matcher ──────────────────────────────────────────
        def matches_any(self, *patterns) -> bool:
            """
            Ultra‑fast одноуровневое сравнение.

            • `matches_any("proton")`
            • `matches_any("proton", "foo:1-2")`
            • `matches_any(("proton", "foo:1-2"))`
            """
            # ---------- нормализация аргументов ----------
            if len(patterns) == 1 and not isinstance(patterns[0], str):
                patterns_iter = patterns[0]           # iterable
            else:
                patterns_iter = patterns              # *args

            nm = self._name
            vr = self._ver_raw

            # ---------- основной цикл ----------
            for p in patterns_iter:
                pat = _compile_leaf_pattern(p)

                # имя
                if pat.name is not None and pat.name != nm:
                    continue

                # требуем last
                if pat.need_last:
                    if vr is not None:
                        continue
                    return True

                # диапазон / одиночная версия / wildcard
                if pat.ver.contains(vr):
                    return True

            return False

        # --------------------------------------------------------------
        def __repr__(self) -> str:
            return f"<Proto {self._name}:{self.version()}>"

    # -------- accessors returning cached leaf objects --------
    @property
    def gn(self) -> _LeafProto:          # noqa: D401
        """Top‑level 'gn' protocol."""
        return self._gn_leaf

    @property
    def connection(self) -> _LeafProto:
        return self._conn_leaf

    @property
    def route(self) -> _LeafProto:
        return self._route_leaf

    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<GNProtocol gn:{self.gn_ver_raw or 'last'} "
            f"{self.conn_name}:{self.conn_ver_raw or 'last'} "
            f"{self.route_name}:{self.route_ver_raw or 'last'}>"
        )
