# 兆迪聯智科技有限公司
# 一般公司請假與晚到通知系統

這是一個可執行的 Django 原型，適合先在內部展示與小範圍試辦。

## 已完成功能

### 員工
- 登入
- 新增請假（僅一般員工）
- 上傳 PDF 或圖片附件
- 查看請假狀態
- 取消待審核申請
- 查看假期餘額
- 發送晚到通知
- 查看晚到通知紀錄

### 主管
- 專用管理 Dashboard（不顯示新增請假）
- 團隊統計卡片與本月審核概況
- 查看待審核請假
- 核准請假
- 退回請假並填寫原因
- 查看當日晚到通知
- 標記晚到通知為已查看
- 匯出請假 CSV

### 管理者
- Django 管理後台
- 管理帳號、角色與直屬主管
- 管理假別
- 管理假期額度
- 查詢請假、晚到與審核紀錄

---

## Windows 快速啟動

### 方法一：雙擊批次檔

雙擊：

```text
快速啟動_Windows.bat
```

第一次啟動會：

1. 建立虛擬環境
2. 安裝 Django
3. 建立資料庫
4. 建立展示資料
5. 啟動網站

瀏覽器開啟：

```text
http://127.0.0.1:8000
```

### 方法二：手動執行

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

---

## macOS / Linux

```bash
chmod +x 快速啟動_macOS_Linux.sh
./快速啟動_macOS_Linux.sh
```

---

## 展示帳號

| 角色 | 帳號 | 密碼 |
|---|---|---|
| 員工 | `employee` | `demo1234` |
| 主管 | `manager` | `demo1234` |
| 管理者 | `admin` | `demo1234` |

管理後台：

```text
http://127.0.0.1:8000/admin/
```

---

## 專案結構

```text
config/                 Django 專案設定
leaveapp/               請假與晚到功能
templates/              HTML 畫面
static/css/             樣式
media/                  上傳附件
docs/                   專案文件
db.sqlite3              執行 migrate 後產生
```

---

## 第一版限制

- 目前使用 SQLite，適合原型與小型內部使用。
- Bootstrap 使用 CDN；無網路時功能仍可操作，但畫面樣式可能較簡單。
- 假期時數採開始與結束時間直接相減，尚未扣除午休或國定假日。
- 不含 Email 寄信功能。
- 不含打卡或薪資系統串接。
- 正式上線前需修改 `SECRET_KEY`、關閉 `DEBUG`，並設定 HTTPS、備份與權限政策。

---

## 建議展示順序

1. 用員工帳號登入並新增一筆請假。
2. 登出後用主管帳號登入。
3. 在待審核清單開啟申請並核准。
4. 再用員工帳號查看核准結果與餘額。
5. 示範晚到通知。
6. 用主管帳號查看當日晚到通知。


## Demo 升級重點

- 主管帳號只顯示管理功能，不可新增請假或晚到通知。
- 主管首頁包含待辦、晚到、管理人數、本月核准數與核准率。
- `seed_demo` 會建立 4 位展示員工、待審申請、已核准／退回紀錄與晚到通知。
- 若舊資料庫已建立，可刪除 `db.sqlite3` 後重新執行啟動檔，取得完整 Demo 資料。
