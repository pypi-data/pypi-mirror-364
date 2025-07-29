# 📚 文件部署指南

本專案已經設定好了完整的文件系統，支援自動部署到 GitHub Pages 和 Read the Docs。

## 🚀 快速部署步驟

### 1. 推送到 GitHub

```bash
# 確保所有文件都已提交
git add .
git commit -m "docs: add comprehensive documentation system with Sphinx and MyST"
git push origin master
```

### 2. 啟用 GitHub Pages

1. 前往你的 GitHub 倉函式庫
2. 點擊 `Settings` 標籤
3. 滾動到 `Pages` 部分
4. 在 `Source` 下拉選單中選擇 `GitHub Actions`
5. 保存設定

### 3. 查看部署狀態

- 前往倉函式庫的 `Actions` 標籤查看構建狀態
- 文件將自動部署到：`https://HYChou0515.github.io/autocrud/`

## 📖 Read the Docs 部署 (可選，推薦)

### 優勢
- 更專業的文件託管
- 支援版本控制
- 更好的搜索功能
- 自訂域名支援

### 設定步驟

1. **註冊帳號**：
   - 前往 https://readthedocs.org/
   - 使用 GitHub/GitLab 帳號登錄

2. **導入專案**：
   - 點擊 "Import a Project"
   - 選擇你的 `autocrud` 倉函式庫
   - 點擊 "Next"

3. **設定專案**：
   - 專案名：`autocrud`
   - 描述：`自動產生 CRUD API 的 Python 函式庫`
   - 語言：`繁體中文`
   - 點擊 "Finish"

4. **構建文件**：
   - RTD 會自動使用我們的 `.readthedocs.yaml` 設定
   - 首次構建可能需要幾分鐘
   - 完成後文件將可在：`https://autocrud.readthedocs.io/` 訪問

## 🔧 本地文件開發

### 構建文件

```bash
# 安裝 dependency
uv sync --dev

# 構建 HTML 文件
make html

# 啟動本地服務器
make serve

# 清理構建文件
make clean
```

### 實時預覽 (可選)

```bash
# 安裝 sphinx-autobuild
uv add --dev sphinx-autobuild

# 啟動實時預覽
make livehtml
```

## 📝 文件結構

```
docs/
├── source/
│   ├── conf.py              # Sphinx 設定
│   ├── index.md             # 主頁
│   ├── quickstart.md        # 快速入門
│   ├── installation.md     # 安裝指南
│   ├── user_guide.md       # 使用者指南
│   ├── api_reference.md    # API 參考
│   ├── examples.md         # 範例集合
│   ├── contributing.md     # 貢獻指南
│   └── changelog.md        # 變更日誌
└── build/
    └── html/               # 構建輸出
```

## 🛠️ 技術棧

- **Sphinx**: 文件產生引擎
- **MyST-Parser**: Markdown 支援
- **Furo**: 現代化主題
- **sphinx-autodoc-typehints**: 自動 API 文件
- **GitHub Actions**: 自動化 CI/CD

## 🔄 更新文件

每次推送到 master 分支時：

1. GitHub Actions 會自動觸發
2. 構建新的文件
3. 部署到 GitHub Pages
4. Read the Docs 也會自動更新 (如果有設定)

## 📊 監控和維護

### 檢查構建狀態

```bash
# 檢查文件連結
make linkcheck

# 執行文件測試
uv run sphinx-build -b doctest docs/source docs/build/doctest
```

### 常見問題

1. **構建失敗**：檢查 Actions 日誌
2. **連結失效**：執行 `make linkcheck`
3. **樣式問題**：清理緩存 `make clean && make html`

## 🎯 下一步

1. push 程式碼到 GitHub
2. 啟用 GitHub Pages
3. (可選) 設定 Read the Docs
4. 自訂域名 (如果需要)
5. 新增徽章到 README

## 📈 徽章範例

可以在 README.md 中新增這些徽章：

```markdown
[![Documentation Status](https://readthedocs.org/projects/autocrud/badge/?version=latest)](https://autocrud.readthedocs.io/en/latest/?badge=latest)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://HYChou0515.github.io/autocrud/)
```
