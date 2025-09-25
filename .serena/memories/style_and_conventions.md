# コード規約と命名

- Python: 3.8+、インデント 4 スペース（`.editorconfig` 準拠）。
- モジュール名: `snake_case`（例: `jp_prefecture_localization`）。
- 既存モデル拡張を優先（例: `res.partner`）。カスタムモデルは `_name='x_module.model_name'` 形式で安定維持。
- XML/QWeb: 説明的な `id` を付与。ビューは小さく分割し再利用可能に。
- 翻訳: 各モジュールの `i18n/ja.po` で日本語文字列を管理。
- テスト: `<module>/tests/test_*.py`、`TransactionCase`/`SavepointCase` を使用。外部副作用を避ける。
- セキュリティ: アクセス権を定義し、秘密情報はコミットしない（環境変数で注入）。

## コミット/PR
- コミットメッセージ: `[module_name] Imperative summary`（例: `[sasuke_backend_theme] Fix kanban alignment`）。
- PR には目的・範囲・UI 変更のスクショ・テスト計画・関連 Issue を記載。
- 変更は最小限、モジュール間の過度な依存を避ける。
