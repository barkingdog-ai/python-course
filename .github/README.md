# gitea

本目錄包含專案的 GiTea CI/CD 工作流程設定，用於自動化程式碼檢查流程。

## workflows

### 程式碼品質檢查 (`check.yml`)

自動執行程式碼品質檢查。

1. 程式碼格式檢查 (ruff format & ruff check)
2. 型別檢查 (mypy)

**觸發條件**：

- 針對所有分支的 PR
