# Acoona Base Translations

本モジュールは Odoo 16 の標準モジュール `base`/`purchase` 向け日本語翻訳 (`i18n/ja_JP.csv`) と、社内テーマ `acoona_theme` の固定文言を一括適用するための配布パッケージです。`purchase.menu_purchase_root` など JSON ベースで保持されるメニュー名もデータ更新で上書きし、インストール直後から「仕入」表記を保証します。

## インストール手順

1. リポジトリを更新後、Docker 環境を起動します。
2. 翻訳モジュールをインストールまたは更新します。

```bash
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i acoona_l10n_base_translations --stop-after-init
```

すでにインストール済みの場合は `-u acoona_l10n_base_translations` で翻訳が再読み込みされます。

> 注記: 本モジュールはインストール/更新時にポストフックで `i18n/ja_JP.csv` を強制上書き読み込みします。`--i18n-overwrite` の指定は不要です。

`post_init_hook` に加えて `post_load` でも翻訳を適用するため、`-u acoona_l10n_base_translations` 実行後や Odoo 再起動時にも翻訳レコードが最新化されます。

## 翻訳更新フロー

1. 英文ソース更新確認:
   - `docker compose exec odoo odoo -c /etc/odoo/odoo.conf --i18n-export=tmp/base.pot --modules=base`
   - 差分を確認し、新規/変更メッセージIDを特定します。
2. `odoo16_base_ja.po` の最新版を取得し、CSV 形式 (`i18n/ja_JP.csv`) へ統合します。
3. テーマ固有の翻訳 (`MENU` など) が欠落していないか確認し、必要に応じて CSV に追記します。
4. コミット前に `git diff` を確認し、翻訳以外の差分が混入していないことを確認します。
5. `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u acoona_l10n_base_translations --stop-after-init` を実行し、翻訳が正しく適用されることを UI で確認します。

## テスト観点

- 言語を日本語に切り替え、メインメニューや `acoona_theme` のサイドバーに日本語翻訳が反映されていること。
- 主要アプリ (設定、販売、会計、仕入など) のメニュー項目が `i18n/ja_JP.csv` に沿った訳語になっていること。
- 仕入アプリのルートメニューが `Purchase` ではなく `仕入` と表示されること。
- 既存環境に登録済みのカスタム翻訳が上書きされていないこと (`ir.translation` レコードの `noupdate` 有無を確認)。

## メンテナンス

- 半期ごと、または Odoo の定例アップデートに合わせて翻訳差分をレビューする。必要に応じて `docs/translation_audit_YYYYMMDD.md` に結果を記載する。
- 追加で翻訳が必要なテーマ/モジュールが発生した場合は、本モジュールの `depends` と `i18n/ja_JP.csv` に追記し、要件定義書 `docs/base_translation_module_requirements.md` を更新する。
