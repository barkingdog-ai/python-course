# python-course

Python 與 uv、ruff、mypy 等練習

## 環境配置

1. 安裝 [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. 使用 `make install` 來安裝需要的套件，並用 `source .venv/bin/activate` 進入環境
3. 使用 `pre-commit install` 開啟 pre-commit，並用 `pre-commit run --all-files` 執行首次檢查
4. 在 `.env` 設定環境變數

## 執行程式

- `make run_api`: 啟動 Uvicorn API 伺服器
- `make run_app`: 啟動 Streamlit 網頁伺服器
