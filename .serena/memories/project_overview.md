# プロジェクト概要

- 目的: Odoo 16 を日本向けにローカライズする各種アドオンを提供する。
- 対象: 開発者が Docker 上で Odoo 16 + PostgreSQL を起動し、`addons/` 配下のモジュールを追加・更新・テストできるようにする。
- 主要スタック: Odoo 16 / Python 3.8+ / PostgreSQL / Docker Compose。
- 稼働ポート: 8069（`docker-compose.yml`）。設定は `config/odoo.conf`。
- エントリ: `docker compose up -d` で起動、Web は `http://localhost:8069`。

## ディレクトリ構成（抜粋）
- `addons/`: カスタムモジュール群（各モジュールは専用ディレクトリ）。
- `config/odoo.conf`: Odoo サーバ設定。
- `docker-compose.yml`: Odoo + PostgreSQL の開発スタック。
- `docs/`: ドキュメント（例: `docs/bank-account-requirements.md`）。
- `.editorconfig`: エディタ統一設定。
- `install_module.py`: インストール補助スクリプト（任意）。

## 既存モジュール（現状）
- `discuss_customization`
- `l10n_jp_partner_title_qweb`
- `mail_debrand`
- `jp_prefecture_localization`
- `jp_bank_localization`
- `sasuke_backend_theme`
- `code_backend_theme`
- `report_alternative_layout`
- `portal_odoo_debranding`
- `sasuke_backend_theme2`
- `l10n_jp_address_layout`
- `jp_bank_account_minimal`
- `remove_odoo_enterprise`

## 開発の基本方針
- 変更は `addons/` 配下のモジュール単位で行い、Odoo コアは改変しない。
- 秘密情報はコミットしない（環境変数で注入）。
- `config/odoo.conf` とポート 8069 の競合に注意。
- テストは Odoo 標準 `TransactionCase` / `SavepointCase` を用いる。
