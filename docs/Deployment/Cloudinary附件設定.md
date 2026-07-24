# Cloudinary 附件永久儲存設定

## 為什麼需要設定

Render 一般 Web Service 的本機檔案系統不是永久儲存空間。若把員工附件放在 `media/`，重新部署或服務重啟後，檔案可能消失，但資料庫仍保留舊路徑，造成 Not Found。

## Cloudinary 設定流程

1. 建立 Cloudinary 帳號。
2. 在 Cloudinary Console 的 API Keys 頁面複製 `CLOUDINARY_URL`。
3. 到 Render：
   - Dashboard
   - 選擇本專案 Web Service
   - Environment
   - Add Environment Variable
4. Key 填：

   `CLOUDINARY_URL`

5. Value 貼上 Cloudinary 提供的完整內容，格式類似：

   `cloudinary://API_KEY:API_SECRET@CLOUD_NAME`

6. 儲存後按 `Manual Deploy → Deploy latest commit`。
7. 使用員工帳號上傳一張新圖片或 PDF，主管開啟附件測試。

## 安全注意事項

- `CLOUDINARY_URL` 含 API Secret，不可寫進 GitHub。
- 不要把真實值放入 `.env.example`。
- 舊附件已經從 Render 消失時無法自動復原，需要原申請人重新上傳。

## 本機行為

本機沒有設定 `CLOUDINARY_URL` 時，附件仍存入 `media/`，方便離線開發。設定後則會改存 Cloudinary。
