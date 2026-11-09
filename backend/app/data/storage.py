"""Lớp truy cập dữ liệu thô (storage).

Toàn bộ backend chỉ phụ thuộc vào bốn thao tác rất nhỏ:

    vertices(collection)        -> đọc tất cả document của một collection
    vertex(collection, key)     -> đọc một document theo key
    edges(collection, from/to)  -> đọc cạnh, lọc được theo _from hoặc _to
    counts()                    -> số bản ghi từng collection

Nhờ vậy phần "nghiệp vụ" (Skill Gap, prerequisite, learning path...) chỉ
viết MỘT lần trong `core.py`, còn hai lớp bên dưới chỉ khác nhau ở chỗ:

    JsonlStorage   -> đọc 12 file .jsonl trong data/ (không cần DB)
    ArangoStorage  -> gửi AQL sang ArangoDB qua HTTP (cần DB thật)

Đây là kiểu kiến trúc "repository": đổi nguồn dữ liệu mà không đổi logic
hay API.
"""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Protocol

from ..schema import ALL_COLLECTIONS, EDGE_COLLECTIONS, VERTEX_COLLECTIONS

Raw = dict[str, Any]


class StorageError(RuntimeError):
    """Không đọc được dữ liệu (thiếu file, DB không trả lời...)."""


class Storage(Protocol):
    """Giao diện tối thiểu mà `CatalogCore` cần.

    Dùng `Protocol` (structural typing) để không phải kế thừa cứng: lớp nào
    có đủ các phương thức này là dùng được.
    """

    mode: str

    def vertices(self, collection: str) -> list[Raw]: ...

    def vertex(self, collection: str, key: str) -> Raw | None: ...

    def edges(
        self,
        collection: str,
        *,
        from_id: str | None = None,
        to_id: str | None = None,
    ) -> list[Raw]: ...

    def counts(self) -> dict[str, int]: ...

    def close(self) -> None: ...


# ==========================================================================
# 1. JSONL trên đĩa
# ==========================================================================
class JsonlStorage:
    """Đọc 12 collection trực tiếp từ file JSONL đã trích xuất.

    Dữ liệu chỉ ~1.6 nghìn bản ghi nên nạp hết vào RAM là hợp lý: đọc một
    lần, trả lời mọi request sau đó trong vài mili-giây.
    """

    mode = "jsonl"

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self._records: dict[str, list[Raw]] = {}
        self._vertex_index: dict[str, dict[str, Raw]] = {}
        self._edge_by_from: dict[str, dict[str, list[Raw]]] = {}
        self._edge_by_to: dict[str, dict[str, list[Raw]]] = {}
        self._loaded = False

    # -- nạp dữ liệu -------------------------------------------------------
    def load(self) -> "JsonlStorage":
        if self._loaded:
            return self
        if not self.data_dir.is_dir():
            raise StorageError(
                f"Không thấy thư mục dữ liệu '{self.data_dir}'. "
                "Chạy: python scripts/extract_dump.py"
            )
        for collection in ALL_COLLECTIONS:
            rows = self._read_collection(collection)
            self._records[collection] = rows
            if collection in VERTEX_COLLECTIONS:
                self._vertex_index[collection] = {str(r["_key"]): r for r in rows}
            if collection in EDGE_COLLECTIONS:
                by_from: dict[str, list[Raw]] = {}
                by_to: dict[str, list[Raw]] = {}
                for row in rows:
                    by_from.setdefault(str(row["_from"]), []).append(row)
                    by_to.setdefault(str(row["_to"]), []).append(row)
                self._edge_by_from[collection] = by_from
                self._edge_by_to[collection] = by_to
        self._loaded = True
        return self

    def _read_collection(self, collection: str) -> list[Raw]:
        path = self.data_dir / f"{collection}.jsonl"
        if not path.is_file():
            raise StorageError(
                f"Thiếu file dữ liệu '{path}'. Chạy: python scripts/extract_dump.py"
            )
        text = path.read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    # -- giao diện đọc -----------------------------------------------------
    def vertices(self, collection: str) -> list[Raw]:
        return self._records.get(collection, [])

    def vertex(self, collection: str, key: str) -> Raw | None:
        return self._vertex_index.get(collection, {}).get(key)

    def edges(
        self,
        collection: str,
        *,
        from_id: str | None = None,
        to_id: str | None = None,
    ) -> list[Raw]:
        if from_id and to_id:
            return [
                row
                for row in self._edge_by_from.get(collection, {}).get(from_id, [])
                if row["_to"] == to_id
            ]
        if from_id:
            return list(self._edge_by_from.get(collection, {}).get(from_id, []))
        if to_id:
            return list(self._edge_by_to.get(collection, {}).get(to_id, []))
        return self._records.get(collection, [])

    def counts(self) -> dict[str, int]:
        return {name: len(rows) for name, rows in self._records.items()}

    def close(self) -> None:
        """Không giữ tài nguyên ngoài RAM -> không cần dọn."""


# ==========================================================================
# 2. ArangoDB qua HTTP (chỉ dùng thư viện chuẩn, không thêm dependency)
# ==========================================================================
class ArangoError(StorageError):
    pass


class ArangoStorage:
    """Đọc ArangoDB bằng AQL qua HTTP.

    Cố tình KHÔNG có hàm ghi: phần đọc dùng AQL, phần ghi do admin làm trên
    ArangoDB Web Interface hoặc qua endpoint CRUD riêng (xem core.py).
    """

    mode = "arango"

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        database: str,
        timeout: float = 3.0,
    ) -> None:
        self.host = host.rstrip("/")
        self.username = username
        self.password = password
        self.database = database
        self.timeout = timeout
        self.server_version: str | None = None

    # -- hạ tầng HTTP ------------------------------------------------------
    def _request(self, method: str, path: str, payload: Any = None) -> Any:
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        token = base64.b64encode(
            f"{self.username}:{self.password}".encode("utf-8")
        ).decode("ascii")
        headers["Authorization"] = f"Basic {token}"
        request = urllib.request.Request(
            f"{self.host}{path}", data=body, method=method, headers=headers
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            try:
                detail = json.loads(exc.read().decode("utf-8"))
            except Exception:  # noqa: BLE001 - body lỗi không parse được
                detail = {}
            message = detail.get("errorMessage") or exc.reason
            raise ArangoError(
                f"ArangoDB {method} {path} → HTTP {exc.code}: {message}"
            ) from exc
        except urllib.error.URLError as exc:
            raise ArangoError(f"Không kết nối được ArangoDB {self.host}: {exc.reason}") from exc
        if not raw:
            return {}
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and parsed.get("error"):
            raise ArangoError(f"AQL lỗi: {parsed.get('errorMessage', parsed)}")
        return parsed

    def _db(self, suffix: str) -> str:
        name = urllib.parse.quote(self.database, safe="")
        return f"/_db/{name}{suffix}"

    def aql(self, query: str, bind_vars: dict[str, Any] | None = None) -> list[Any]:
        """Chạy AQL và tự động nối các batch khi kết quả lớn."""
        rows: list[Any] = []
        result = self._request(
            "POST",
            self._db("/_api/cursor"),
            {"query": query, "bindVars": bind_vars or {}, "batchSize": 1000},
        )
        rows.extend(result.get("result", []))
        while result.get("hasMore"):
            cursor = urllib.parse.quote(str(result["id"]), safe="")
            result = self._request("PUT", self._db(f"/_api/cursor/{cursor}"), {})
            rows.extend(result.get("result", []))
        return rows

    # -- kiểm tra kết nối --------------------------------------------------
    def ping(self) -> bool:
        try:
            info = self._request("GET", "/_api/version")
        except (ArangoError, json.JSONDecodeError):
            return False
        self.server_version = str(info.get("version", "unknown"))
        # Xác nhận database đích tồn tại và truy vấn được.
        self._request("GET", self._db("/_api/collection"))
        return True

    # -- giao diện đọc -----------------------------------------------------
    def vertices(self, collection: str) -> list[Raw]:
        return self.aql("FOR doc IN @@collection RETURN doc", {"@collection": collection})

    def vertex(self, collection: str, key: str) -> Raw | None:
        rows = self.aql("RETURN DOCUMENT(@id)", {"id": f"{collection}/{key}"})
        return rows[0] if rows and rows[0] else None

    def edges(
        self,
        collection: str,
        *,
        from_id: str | None = None,
        to_id: str | None = None,
    ) -> list[Raw]:
        if from_id and to_id:
            query = "FOR e IN @@c FILTER e._from == @f AND e._to == @t RETURN e"
            binds: dict[str, Any] = {"@c": collection, "f": from_id, "t": to_id}
        elif from_id:
            query = "FOR e IN @@c FILTER e._from == @f RETURN e"
            binds = {"@c": collection, "f": from_id}
        elif to_id:
            query = "FOR e IN @@c FILTER e._to == @t RETURN e"
            binds = {"@c": collection, "t": to_id}
        else:
            query = "FOR e IN @@c RETURN e"
            binds = {"@c": collection}
        return self.aql(query, binds)

    def counts(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for collection in ALL_COLLECTIONS:
            try:
                value = self.aql("RETURN LENGTH(@@c)", {"@c": collection})
                result[collection] = int(value[0]) if value else 0
            except (ArangoError, ValueError, TypeError, IndexError):
                result[collection] = 0
        return result

    def close(self) -> None:
        """urllib không giữ connection pool -> không cần đóng."""


# ==========================================================================
# 3. Chọn backend theo cấu hình
# ==========================================================================
def build_storage(settings) -> tuple[JsonlStorage | ArangoStorage, dict[str, Any]]:
    """Trả về (storage, thông tin chẩn đoán).

    auto   : thử ArangoDB trước, thất bại thì dùng JSONL (không làm sập app).
    jsonl  : chỉ đọc file.
    arango : bắt buộc ArangoDB, thất bại thì raise -> người vận hành biết ngay.
    """
    diagnostics: dict[str, Any] = {
        "mode": settings.mode,
        "arango": {
            "configured": settings.mode != "jsonl",
            "connected": False,
            "host": settings.arango_host,
            "database": settings.arango_database,
            "server_version": None,
            "error": None,
        },
    }

    if settings.mode != "jsonl":
        arango = ArangoStorage(
            host=settings.arango_host,
            username=settings.arango_user,
            password=settings.arango_password,
            database=settings.arango_database,
            timeout=settings.arango_timeout,
        )
        try:
            if arango.ping():
                diagnostics["arango"].update(
                    {"connected": True, "server_version": arango.server_version}
                )
                return arango, diagnostics
            diagnostics["arango"]["error"] = "ArangoDB không phản hồi."
        except ArangoError as exc:
            diagnostics["arango"]["error"] = str(exc)
        if settings.mode == "arango":
            raise StorageError(
                "SKILLGRAPH_DATA_MODE=arango nhưng không kết nối được ArangoDB: "
                f"{diagnostics['arango']['error']}"
            )

    jsonl = JsonlStorage(settings.data_dir).load()
    return jsonl, diagnostics
