#!/usr/bin/env bash
# =====================================================================
#  SKILL GRAPH - Khoi dong he thong (macOS / Linux)
#  Cach dung:  bash CHAY_NGAY.sh
# =====================================================================
set -u

cd "$(dirname "$0")"

echo
echo "============================================================"
echo "   SKILL GRAPH - HE THONG DE XUAT LO TRINH HOC CA NHAN HOA"
echo "============================================================"
echo

# ---------------------------------------------------------------------
#  BUOC 1: Tim Python
# ---------------------------------------------------------------------
echo "[1/4] Kiem tra Python..."

PY=""
for cand in python3 python; do
    if command -v "$cand" >/dev/null 2>&1; then
        major=$("$cand" -c 'import sys;print(sys.version_info[0])' 2>/dev/null || echo "")
        if [ "$major" = "3" ]; then
            PY="$cand"
            break
        fi
    fi
done

if [ -z "$PY" ]; then
    echo
    echo "------------------------------------------------------------"
    echo "  KHONG TIM THAY PYTHON"
    echo "------------------------------------------------------------"
    echo
    echo "  Cach sua:"
    echo "    - macOS :  brew install python@3.12"
    echo "    - Ubuntu:  sudo apt install python3 python3-pip python3-venv"
    echo "    - Khac   :  https://www.python.org/downloads/"
    echo
    echo "------------------------------------------------------------"
    exit 1
fi

echo "      OK - da tim thay $($PY -c 'import sys;print(sys.version.split()[0])')"

# ---------------------------------------------------------------------
#  BUOC 2: Cai thu vien
# ---------------------------------------------------------------------
echo
echo "[2/4] Kiem tra thu vien (fastapi, uvicorn, pydantic)..."

if ! "$PY" -c "import fastapi, uvicorn, pydantic" >/dev/null 2>&1; then
    echo "      Thieu thu vien - dang cai dat (co the mat 1-2 phut)..."

    # macOS Homebrew va Ubuntu moi deu chan pip cai thang vao he thong.
    # Dung virtualenv cho chac chan.
    if [ ! -d ".venv" ]; then
        "$PY" -m venv .venv 2>/dev/null || true
    fi
    if [ -x ".venv/bin/python" ]; then
        PY=".venv/bin/python"
        "$PY" -m pip install --upgrade pip --quiet --disable-pip-version-check
    fi

    if ! "$PY" -m pip install -r backend/requirements.txt --quiet --disable-pip-version-check; then
        echo
        echo "------------------------------------------------------------"
        echo "  CAI THU VIEN THAT BAI"
        echo "------------------------------------------------------------"
        echo
        echo "  Thu chay tay lenh sau de xem loi chi tiet:"
        echo "      $PY -m pip install -r backend/requirements.txt"
        echo
        echo "------------------------------------------------------------"
        exit 1
    fi
    echo
    echo "      OK - da cai xong thu vien."
else
    echo "      OK - thu vien da co san."
fi

# ---------------------------------------------------------------------
#  BUOC 3: Kiem tra du lieu
# ---------------------------------------------------------------------
echo
echo "[3/4] Kiem tra du lieu..."

if [ ! -f "data/manifest.json" ]; then
    echo
    echo "------------------------------------------------------------"
    echo "  THIEU THU MUC DU LIEU"
    echo "------------------------------------------------------------"
    echo
    echo "  Khong tim thay: data/manifest.json"
    echo "  Ban tai thieu file. Hay tai lai toan bo repo:"
    echo "      https://github.com/phupatrick/skill-graph-arangodb"
    echo
    echo "------------------------------------------------------------"
    exit 1
fi

echo "      OK - tim thay $(ls -1 data/*.jsonl 2>/dev/null | wc -l | tr -d ' ') file du lieu."

# ---------------------------------------------------------------------
#  BUOC 4: Khoi dong
# ---------------------------------------------------------------------
echo
echo "[4/4] Dang khoi dong may chu..."
echo
echo "============================================================"
echo "   DIA CHI SU DUNG"
echo "============================================================"
echo
echo "   Giao dien demo   :  http://127.0.0.1:8000/demo"
echo "   Tai lieu API     :  http://127.0.0.1:8000/docs"
echo "   Kiem tra he thong :  http://127.0.0.1:8000/api/v1/meta/health"
echo
echo "   DE TAT: bam Ctrl+C"
echo
echo "============================================================"
echo

cd backend
exec "$PY" run.py
