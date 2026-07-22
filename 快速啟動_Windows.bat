@echo off
chcp 65001 >nul
cd /d %~dp0

if not exist .venv (
  echo 建立虛擬環境...
  python -m venv .venv
)

call .venv\Scripts\activate

echo 安裝套件...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo 建立資料庫...
python manage.py makemigrations
python manage.py migrate

echo 建立展示資料...
python manage.py seed_demo

echo.
echo 系統啟動：http://127.0.0.1:8000
echo 員工 employee / demo1234
echo 主管 manager / demo1234
echo 管理者 admin / demo1234
echo.
python manage.py runserver
pause
