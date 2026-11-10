@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
title Skill Graph - Chay ca Backend va Frontend

cd /d "%~dp0"

echo.
echo ============================================================
echo    SKILL GRAPH - CHAY CA BACKEND (Python) VA FRONTEND (React)
echo ============================================================
echo.
echo  Script nay mo 2 cua so:
echo    - Cua so 1: Backend Python  (cong 8000)
echo    - Cua so 2: Frontend React  (cong 5173)
echo.
echo  Sau khi ca hai chay xong, trinh duyet se tu mo.
echo.

REM ------------------------------------------------------------------
REM  BUOC 1: Tim Python
REM ------------------------------------------------------------------
echo [1/5] Kiem tra Python...

set "PY="
set "PYVER="

where python >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%v in ('python -c "import sys;print(sys.version_info[0])" 2^>nul') do set "PYVER=%%v"
    if "!PYVER!"=="3" set "PY=python"
)
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
    echo   1. Vao https://www.python.org/downloads/
    echo   2. Tai Python 3.11 tro len
    echo   3. Khi cai, TICH vao o:  [x] Add python.exe to PATH
    echo   4. Tat cua so nay, bam lai CHAY_CA_HAI.bat
    echo.
    echo ------------------------------------------------------------
    pause
    exit /b 1
)
echo       OK - da tim thay Python.

REM ------------------------------------------------------------------
REM  BUOC 2: Thu vien Python
REM ------------------------------------------------------------------
echo.
echo [2/5] Kiem tra thu vien Python...

%PY% -c "import fastapi, uvicorn, pydantic" >nul 2>&1
if errorlevel 1 (
    echo       Thieu thu vien - dang cai dat...
    %PY% -m pip install --upgrade pip --quiet --disable-pip-version-check
    %PY% -m pip install -r backend\requirements.txt --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo.
        echo ------------------------------------------------------------
        echo   CAI THU VIEN PYTHON THAT BAI
        echo ------------------------------------------------------------
        echo   Thu chay tay:  %PY% -m pip install -r backend\requirements.txt
        echo ------------------------------------------------------------
        pause
        exit /b 1
    )
)
echo       OK - thu vien Python da san sang.

REM ------------------------------------------------------------------
REM  BUOC 3: Node.js cho frontend
REM ------------------------------------------------------------------
echo.
echo [3/5] Kiem tra Node.js...

where node >nul 2>&1
if errorlevel 1 (
    echo.
    echo ------------------------------------------------------------
    echo   KHONG TIM THAY NODE.JS
    echo ------------------------------------------------------------
    echo.
    echo   Frontend React CAN Node.js de chay.
    echo.
    echo   1. Vao https://nodejs.org/
    echo   2. Tai ban "LTS" ^(khuyen dung^)
    echo   3. Cai dat binh thuong ^(bam Next lien tuc^)
    echo   4. Tat cua so nay, bam lai CHAY_CA_HAI.bat
    echo.
    echo   GHI CHU: neu chi muon xem giao dien demo HTML, dung
    echo   CHAY_NGAY.bat ^(khong can Node.js^).
    echo.
    echo ------------------------------------------------------------
    pause
    exit /b 1
)
for /f "delims=" %%v in ('node --version 2^>nul') do echo       OK - Node.js %%v

REM ------------------------------------------------------------------
REM  BUOC 4: node_modules
REM ------------------------------------------------------------------
echo.
echo [4/5] Kiem tra thu vien frontend ^(node_modules^)...

if not exist "frontend\node_modules" (
    echo       Chua co node_modules - dang cai dat...
    echo       ^(lan dau co the mat 1-3 phut^)
    echo.
    pushd frontend
    call npm install --no-audit --no-fund
    set "NPMERR=!errorlevel!"
    popd
    if not "!NPMERR!"=="0" (
        echo.
        echo ------------------------------------------------------------
        echo   CAI THU VIEN FRONTEND THAT BAI
        echo ------------------------------------------------------------
        echo   Thu chay tay:
        echo       cd frontend
        echo       npm install
        echo ------------------------------------------------------------
        pause
        exit /b 1
    )
    echo.
    echo       OK - da cai xong.
) else (
    echo       OK - node_modules da co san.
)

REM ------------------------------------------------------------------
REM  Tao .env.local neu chua co
REM ------------------------------------------------------------------
if not exist "frontend\.env.local" (
    > "frontend\.env.local" echo VITE_DATA_SOURCE=api
    >> "frontend\.env.local" echo VITE_API_BASE_URL=http://127.0.0.1:8000/compat
    echo       Da tao frontend\.env.local ^(tro API vao backend^).
)

REM ------------------------------------------------------------------
REM  BUOC 5: Khoi dong
REM ------------------------------------------------------------------
echo.
echo [5/5] Dang khoi dong...
echo.

start "SkillGraph BACKEND (cong 8000)" cmd /k "cd /d "%~dp0backend" && %PY% run.py"

REM Doi backend san sang truoc khi bat frontend
echo       Cho backend khoi dong xong...
timeout /t 6 /nobreak >nul

start "SkillGraph FRONTEND (cong 5173)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

REM Doi frontend san sang roi mo trinh duyet
start "" cmd /c "timeout /t 8 /nobreak >nul & start http://127.0.0.1:5173"

echo.
echo ============================================================
echo    DA KHOI DONG XONG - 2 CUA SO DANG CHAY
echo ============================================================
echo.
echo    FRONTEND ^(giao dien React^)
echo       http://127.0.0.1:5173
echo.
echo    BACKEND ^(API^)
echo       http://127.0.0.1:8000/demo      giao dien demo HTML
echo       http://127.0.0.1:8000/docs      tai lieu API
echo.
echo    Kiem tra da noi dung chua: trang chu frontend phai hien
echo    29 nghe / 248 ky nang / 89 hoc lieu / 0 nhom ESCO / 8 nha
echo    cung cap. Neu thay 12 / 420 / 504 thi frontend dang dung
echo    du lieu local, chua noi vao backend.
echo.
echo    DE TAT: dong ca 2 cua so vua mo.
echo ============================================================
echo.
pause
