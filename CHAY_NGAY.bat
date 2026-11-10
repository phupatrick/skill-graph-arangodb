@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
title Skill Graph - Khoi dong he thong

cd /d "%~dp0"

echo.
echo ============================================================
echo    SKILL GRAPH - HE THONG DE XUAT LO TRINH HOC CA NHAN HOA
echo ============================================================
echo.

REM ------------------------------------------------------------------
REM  BUOC 1: Tim Python
REM ------------------------------------------------------------------
echo [1/4] Kiem tra Python...

set "PY="
set "PYVER="

REM Thu lenh "python" truoc
where python >nul 2>&1
if not errorlevel 1 (
    REM Lenh "python" tren Windows co the la App Execution Alias dan toi
    REM Microsoft Store, khong phai Python that. Phai goi thu de biet chac.
    for /f "delims=" %%v in ('python -c "import sys;print(sys.version_info[0])" 2^>nul') do set "PYVER=%%v"
    if "!PYVER!"=="3" set "PY=python"
)

REM Khong duoc thi thu "py" (Python Launcher, co san khi cai tu python.org)
if not defined PY (
    where py >nul 2>&1
    if not errorlevel 1 (
        for /f "delims=" %%v in ('py -3 -c "import sys;print(sys.version_info[0])" 2^>nul') do set "PYVER=%%v"
        if "!PYVER!"=="3" set "PY=py -3"
    )
)

if not defined PY (
    echo.
    echo ------------------------------------------------------------
    echo   KHONG TIM THAY PYTHON
    echo ------------------------------------------------------------
    echo.
    echo   May nay chua cai Python ^(hoac cai chua dung^).
    echo.
    echo   Cach sua:
    echo     1. Vao https://www.python.org/downloads/
    echo     2. Tai ban Python 3.11 tro len
    echo     3. Khi cai, NHO TICH vao o:
    echo          [x] Add python.exe to PATH
    echo     4. Cai xong, tat cua so nay va bam lai CHAY_NGAY.bat
    echo.
    echo ------------------------------------------------------------
    pause
    exit /b 1
)

for /f "delims=" %%v in ('%PY% -c "import sys;print(sys.version.split()[0])" 2^>nul') do set "PYFULL=%%v"
echo       OK - da tim thay Python !PYFULL!

REM ------------------------------------------------------------------
REM  BUOC 2: Cai thu vien can thiet
REM ------------------------------------------------------------------
echo.
echo [2/4] Kiem tra thu vien ^(fastapi, uvicorn, pydantic^)...

%PY% -c "import fastapi, uvicorn, pydantic" >nul 2>&1
if errorlevel 1 (
    echo       Thieu thu vien - dang cai dat ^(lan dau co the mat 1-2 phut^)...
    echo.
    %PY% -m pip install --upgrade pip --quiet --disable-pip-version-check
    %PY% -m pip install -r backend\requirements.txt --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo.
        echo ------------------------------------------------------------
        echo   CAI THU VIEN THAT BAI
        echo ------------------------------------------------------------
        echo.
        echo   Thu chay tay lenh sau de xem loi chi tiet:
        echo       %PY% -m pip install -r backend\requirements.txt
        echo.
        echo   Nguyen nhan thuong gap:
        echo     - May khong co mang
        echo     - Mang cong ty chan pip ^(thu dung 4G dien thoai^)
        echo.
        echo ------------------------------------------------------------
        pause
        exit /b 1
    )
    echo.
    echo       OK - da cai xong thu vien.
) else (
    echo       OK - thu vien da co san.
)

REM ------------------------------------------------------------------
REM  BUOC 3: Kiem tra du lieu
REM ------------------------------------------------------------------
echo.
echo [3/4] Kiem tra du lieu...

if not exist "data\manifest.json" (
    echo.
    echo ------------------------------------------------------------
    echo   THIEU THU MUC DU LIEU
    echo ------------------------------------------------------------
    echo.
    echo   Khong tim thay: data\manifest.json
    echo.
    echo   Ban tai thieu file. Hay tai lai TOAN BO repo:
    echo       https://github.com/phupatrick/skill-graph-arangodb
    echo   Bam nut "Code" mau xanh roi chon "Download ZIP".
    echo.
    echo ------------------------------------------------------------
    pause
    exit /b 1
)

set "NFILES=0"
for %%f in (data\*.jsonl) do set /a NFILES+=1
echo       OK - tim thay !NFILES! file du lieu.

REM ------------------------------------------------------------------
REM  BUOC 4: Khoi dong
REM ------------------------------------------------------------------
echo.
echo [4/4] Dang khoi dong may chu...
echo.
echo ============================================================
echo    DIA CHI SU DUNG
echo ============================================================
echo.
echo    Giao dien demo   :  http://127.0.0.1:8000/demo
echo    Tai lieu API     :  http://127.0.0.1:8000/docs
echo    Kiem tra he thong :  http://127.0.0.1:8000/api/v1/meta/health
echo.
echo    Trinh duyet se tu mo sau 4 giay.
echo.
echo    DE TAT: dong cua so nay, hoac bam Ctrl+C
echo.
echo ============================================================
echo.

REM Mo trinh duyet sau 4 giay, chay song song nen khong chan server
start "" cmd /c "timeout /t 4 /nobreak >nul & start http://127.0.0.1:8000/demo"

cd backend
%PY% run.py

echo.
echo May chu da dung.
pause
