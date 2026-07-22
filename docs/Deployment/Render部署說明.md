# Render 部署說明

## 本版本定位

這是主管展示用的快速部署版本：

- Django
- Gunicorn
- WhiteNoise
- SQLite Demo Database
- Render HTTPS 公開網址

SQLite 在 Render 免費 Web Service 上不是永久儲存。重新部署或服務環境重建後，線上新增的資料可能消失。正式公司使用時請改成 Render PostgreSQL。

## 上傳 GitHub

在專案根目錄執行：

```powershell
git add .
git commit -m "Sprint 4: 加入 Render 部署設定"
git push origin main
```

## Render 建立服務

1. 登入 Render。
2. 點選 **New +**。
3. 選擇 **Blueprint**。
4. 連接 GitHub Repository：
   `l931206/leave-management-system`
5. Render 會讀取根目錄的 `render.yaml`。
6. 點選 **Apply** 或 **Deploy Blueprint**。
7. 等待 Build 與 Deploy 完成。

## 正常建置紀錄

部署紀錄應看到：

```text
Applying migrations
展示資料建立完成
Running collectstatic
Starting gunicorn
```

## 展示帳號

- 員工：`employee / demo1234`
- 主管：`manager / demo1234`
- 管理者：`admin / demo1234`

## 常見錯誤

### build.sh 權限錯誤

Render 通常可以直接執行。若出現 Permission denied，在 Git Bash 或 WSL 執行：

```bash
git update-index --chmod=+x build.sh
git commit -m "Make build script executable"
git push
```

也可在 Render 的 Build Command 手動填：

```text
bash build.sh
```

### DisallowedHost

確認 Render 環境中存在 `RENDER_EXTERNAL_HOSTNAME`。Render 會自動提供此變數。

### 靜態檔案消失

確認：

- `whitenoise` 已安裝
- `WhiteNoiseMiddleware` 位於 SecurityMiddleware 後方
- Build Log 有成功執行 `collectstatic`
