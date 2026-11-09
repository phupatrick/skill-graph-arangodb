"""Trích xuất dump ArangoDB (skill_graph_db) sang JSONL chuẩn.

Tại sao cần file này?
- Dump là định dạng của `arangodump` (gzip + JSON envelope), không đọc trực
  tiếp bằng code Python thông thường.
- Trích xuất ra JSONL để: (a) phát triển backend mà không cần ArangoDB,
  (b) import lại vào ArangoDB bằng arangoimport nếu cần, (c) kiểm thử.

Chạy:
    python scripts/extract_dump.py
    python scripts/extract_dump.py --dump <duong_dan_dump> --out <thu_muc_dau_ra>
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from pathlib import Path

# Windows console mặc định dùng codepage cp1258/cp437 -> in tiếng Việt sẽ lỗi.
# Ép stdout/stderr sang UTF-8 để chạy được trên mọi máy.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def _collection_name(filename: str) -> str:
    """'skills_a658...data.json.gz' -> 'skills'."""
    base = filename
    if base.endswith(".data.json.gz"):
        base = base[: -len(".data.json.gz")]
    elif base.endswith(".data.json"):
        base = base[: -len(".data.json")]
    parts = base.rsplit("_", 1)
    if len(parts) == 2 and re.fullmatch(r"[0-9a-f]{20,}", parts[1]):
        return parts[0]
    return base


def extract(dump_dir: Path, out_dir: Path) -> dict[str, int]:
    dump_dir = Path(dump_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data_files = sorted(dump_dir.glob("*.data.json.gz"))
    if not data_files:
        data_files = sorted(dump_dir.glob("*.data.json"))
    if not data_files:
        raise SystemExit(f"Không tìm thấy file *.data.json.gz trong {dump_dir}")

    counts: dict[str, int] = {}
    for path in data_files:
        name = _collection_name(path.name)
        target = out_dir / f"{name}.jsonl"
        n = 0
        opener = gzip.open if path.suffix == ".gz" else open
        with opener(path, "rt", encoding="utf-8") as src, target.open(
            "w", encoding="utf-8"
        ) as dst:
            for line in src:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                # Bỏ metadata nội bộ của ArangoDB, giữ _key/_from/_to.
                obj.pop("_rev", None)
                dst.write(json.dumps(obj, ensure_ascii=False) + "\n")
                n += 1
        counts[name] = n
        print(f"  {name:18s} {n:6d} bản ghi -> {target.name}")
    return counts


def main() -> int:
    here = Path(__file__).resolve()
    parser = argparse.ArgumentParser(description="Trích xuất dump ArangoDB sang JSONL")
    parser.add_argument(
        "--dump",
        default=str(here.parents[3] / "_inputs" / "skill_graph_db_dump" / "skill_graph_db_dump"),
        help="Thư mục chứa file dump",
    )
    parser.add_argument(
        "--out",
        default=str(here.parents[2] / "data"),
        help="Thư mục đầu ra",
    )
    args = parser.parse_args()

    dump_dir = Path(args.dump)
    out_dir = Path(args.out)
    if not dump_dir.is_dir():
        print(f"LỖI: không thấy thư mục dump '{dump_dir}'", file=sys.stderr)
        return 1

    print(f"Trích xuất từ: {dump_dir}")
    print(f"Đầu ra     : {out_dir}")
    counts = extract(dump_dir, out_dir)
    total = sum(counts.values())
    print(f"\nTổng cộng: {total} bản ghi trên {len(counts)} collection.")

    manifest = {"collections": counts, "total_records": total}
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
