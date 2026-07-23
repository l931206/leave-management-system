# 兆迪聯智科技有限公司－員工請假與出勤管理系統

以 Django 建置的公司內部管理系統，支援員工請假、晚到通知、主管審核、查詢篩選與 CSV 匯出。

## 主要功能

### 員工
- 線上請假
- 上傳請假附件
- 晚到通知主管
- 查看個人申請狀態與假期餘額

### 主管與系統管理者
- 獨立請假管理頁
- 搜尋與狀態篩選
- 核准或退回請假
- 獨立晚到通知管理頁
- 已讀與未讀篩選
- CSV 匯出

## 技術

- Python / Django
- Django ORM
- SQLite（展示版）
- Bootstrap 5
- Chart.js
- Gunicorn / WhiteNoise
- Render

## 專案結構

```text
config/                  Django 專案設定
leaveapp/                請假與晚到功能
templates/               HTML 模板
static/                  CSS 與 JavaScript
media/                   使用者上傳附件
docs/                    分類文件
scripts/                 快速啟動腳本
screenshots/             GitHub 展示截圖
manage.py                Django 指令入口
requirements.txt         Python 相依套件
render.yaml              Render 部署設定
```

## 本機啟動

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver
```

## 展示帳號

- 員工：`employee / demo1234`
- 主管：`manager / demo1234`
- 管理者：`admin / demo1234`

## 線上展示

`https://leave-management-system-demo.onrender.com`
