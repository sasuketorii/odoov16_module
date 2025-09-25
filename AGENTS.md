# リポジトリガイドライン

本ドキュメントは、Odoo 16 日本向けローカライズ用リポジトリの簡潔なコントリビューターガイドです。ローカルでの作業は必ず Docker を使用し、あらゆるカスタマイズは `addons/` 配下に配置してください。

## プロジェクト構成とモジュール整理
- `addons/`: 各カスタムモジュールは専用ディレクトリを持ちます（例: `addons/acoona_jp_prefecture_localization/`）。配下には `__manifest__.py`、`models/`、`views/`、`security/`、`data/`、`i18n/ja.po`、`static/`、任意で `tests/` を用意します。
- `config/odoo.conf`: コンテナが読み込むサーバー設定。
- `docker-compose.yml`: 開発スタック（PostgreSQL + Odoo 16、ポート `8069`）。
- `docs/`: プロジェクトのドキュメントやメモ。
- `install_module.py`: Odoo 環境が利用可能な場合にモジュールをインストールするヘルパー（任意）。

## ビルド・テスト・開発コマンド
- サービス起動: `docker compose up -d`（DB と Odoo を `8069` で起動）。
- ログ追跡: `docker compose logs -f odoo`。
- 初回インストール: `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --stop-after-init`。
- 既存モジュール更新: `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u <module> --stop-after-init`。
- テスト実行: `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --test-enable --stop-after-init`。

## コーディング規約と命名
- Python 3.8+、インデントは 4 スペース。`.editorconfig` に準拠。
- モジュール名は `snake_case`（例: `acoona_jp_prefecture_localization`）。
- モデル: 既存コア（例: `res.partner`）の拡張を優先。カスタムモデルは `x_module.model_name` の形式とし、安定した `_name` を維持。
- XML/QWeb: 説明的な `id` を付与し、ビューは小さく分割して再利用可能に。
- 翻訳: 日本語文字列は各モジュールの `i18n/ja.po` で管理。

## テスト方針
- テストは `<module>/tests/` 配下に `test_*.py` という名前で配置。
- Odoo の `TransactionCase` または `SavepointCase` を使用し、外部副作用を避ける。
- ドメインロジック、アクセス権、ビューがトレースバックなしでロードできることをカバー。
- 実行は上記テストコマンドを使用。初回は `-i`、更新時は `-u` を指定。

## コミットおよびプルリクエスト
- コミット: `[module_name] Imperative summary`（例: `[sasuke_backend_theme] Fix kanban alignment`）。
- PR には目的・範囲・UI 変更のスクリーンショット・テスト計画・関連 Issue を含める。
- 変更は PR ごとに最小限にし、モジュール間の過度な依存を避ける。

## セキュリティと設定の注意
- 秘密情報はコミットしない。DB/認証は環境変数で設定。
- カスタムコードは `addons/` に限定し、Odoo コアは改変しない。
- `config/odoo.conf` とポート `8069` がローカルの他サービスと競合しないことを確認。

## エージェント運用ポリシー（Codex CLI）
- 既定言語: 回答・説明は日本語（`.condex/config.toml` の `default_language = "ja"` に準拠）。ユーザーが英語を明示した場合のみ英語に切替。
- 表記ルール: コード、CLI コマンド、設定キー、モデル名、ログは原文を保持（英語可）。引用ログや英語エラーには必ず日本語の解説を併記。
- コメント/ドキュメント: コードコメントやドキュメント（本ファイル含む）は日本語で記載。
- 実行プレアンブル: シェル/ファイル操作の前に、日本語で要点のみ 1–2 文のプレアンブルを付記。
- プラン管理: 複数工程の作業は `update_plan` を使用し、常に 1 項目のみを `in_progress` とする。完了時は全項目を `completed` に更新。
- 変更範囲: 変更は最小限・モジュール単位で `addons/` 配下に限定。Odoo コアは編集禁止。
- Docker 準拠: 起動/更新/テストは本書記載の `docker compose` コマンドを使用。
- ネットワーク/ウェブ参照: `.condex` の `network_access = true` と `tools.web_search = true` に整合。ただし実行環境のサンドボックスに従う。変化しやすい情報（価格・ニュース・規約など）は必要に応じて外部参照し、出典を明示。
- セキュリティ: 資格情報はコミットせず、環境変数で受け渡す。
- コミット/PR: 既存規約を優先し、コミットメッセージは英語形式（例: `[module_name] Imperative summary`）。PR 本文や説明は日本語で可。
