# Acoona Base Translations

本モジュールは Odoo 16 の標準モジュール `base` 向け日本語翻訳 (`odoo16_base_ja.po`) と、社内テーマ `acoona_theme` の固定文言を一括適用するための配布パッケージです。

## インストール手順

1. リポジトリを更新後、Docker 環境を起動します。
2. 翻訳モジュールをインストールまたは更新します。

```bash
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i acoona_l10n_base_translations --stop-after-init
```

すでにインストール済みの場合は `-u acoona_l10n_base_translations` で翻訳が再読み込みされます。

## 翻訳更新フロー

1. 英文ソース更新確認:
   - `docker compose exec odoo odoo -c /etc/odoo/odoo.conf --i18n-export=tmp/base.pot --modules=base`
   - 差分を確認し、新規/変更メッセージIDを特定します。
2. `odoo16_base_ja.po` の最新版を取得し、`i18n/ja.po` を置き換えます。
3. テーマ固有の翻訳 (`MENU` など) が欠落していないか確認し、必要に応じて PO 末尾へ追記します。
4. コミット前に `git diff` を確認し、翻訳以外の差分が混入していないことを確認します。
5. `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u acoona_l10n_base_translations --stop-after-init` を実行し、翻訳が正しく適用されることを UI で確認します。

## テスト観点

- 言語を日本語に切り替え、メインメニューや `acoona_theme` のサイドバーに日本語翻訳が反映されていること。
- 主要アプリ (設定、販売、会計など) のメニュー項目が `odoo16_base_ja.po` に沿った訳語になっていること。
- 既存環境に登録済みのカスタム翻訳が上書きされていないこと (`ir.translation` レコードの `noupdate` 有無を確認)。

## メンテナンス

- 半期ごと、または Odoo の定例アップデートに合わせて翻訳差分をレビューする。必要に応じて `docs/translation_audit_YYYYMMDD.md` に結果を記載する。
- 追加で翻訳が必要なテーマ/モジュールが発生した場合は、本モジュールの `depends` と `i18n/ja.po` に追記し、要件定義書 `docs/base_translation_module_requirements.md` を更新する。
