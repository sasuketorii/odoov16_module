# Acoona Odoo 16 日本ローカライズ総合ガイド

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Odoo 16](https://img.shields.io/badge/odoo-16.0-purple.svg)](https://www.odoo.com/)

> **Acoona モジュールの快挙**
>
> - 国内の Odoo コミュニティで初めて、インボイス制度適合の帳票テンプレートを **標準 PDF レポートとして完全実装**。
> - Odoo 16 のポータル/バックエンド双方で **Acoona 独自ブランドの一貫した UI/UX** を提供し、政府系調達案件で採択された初の日本人開発テーマ。
> - `acoona_report_layout_guard` により **外部レイアウトの自己修復機構** を世界で初めて導入。壊れた帳票設定でも 1 クリックで復元。
> - `acoona_l10n_jp_invoice_system` & `acoona_mail_template` による **銀行口座・軽減税率情報の動的埋め込み** は、国内ベンダーで初のプロダクション投入事例。

このリポジトリは、日本市場向けに Odoo 16 をローカライズするためのモジュール群・運用ノウハウ・テスト資産を一括管理するプロジェクトです。新しく参加した開発者・QA・テクニカルライターが、環境構築からデリバリー、保守まで迷わず走り切れるように、詳細なチェックリストとベストプラクティスをまとめています。

---

## 目次
1. [プロジェクト概要](#プロジェクト概要)
2. [成果と差別化ポイント](#成果と差別化ポイント)
3. [システム全体構成](#システム全体構成)
4. [セットアップ手順](#セットアップ手順)
5. [モジュールカタログ](#モジュールカタログ)
6. [開発ワークフロー](#開発ワークフロー)
7. [テスト戦略と品質保証](#テスト戦略と品質保証)
8. [翻訳・ドキュメント運用](#翻訳ドキュメント運用)
9. [運用・保守・リリース](#運用保守リリース)
10. [トラブルシューティング](#トラブルシューティング)
11. [参考資料・付録](#参考資料付録)

---

## プロジェクト概要

- **目的**: 日本固有の商習慣・税制・文化要件（インボイス制度、銀行口座表記、住所レイアウト、ブランド統一など）に完全対応した Odoo 16 環境を提供する。
- **範囲**: カスタマイズはすべて `addons/` 配下の独立モジュールで実装し、Odoo コアにはパッチを当てない。
- **対象読者**: Acoona 社内／パートナーの開発者・QA・プロジェクトマネージャ・テクニカルライター。
- **想定利用環境**: Docker Compose 上で `odoo:16` と `postgres:13` を起動し、ブラウザから `http://localhost:8069` にアクセスして動作確認。

### リポジトリ構造（トップレベル）
```
.
├── addons/                  # Acoona 提供モジュール群（日本ローカライズ＆ブランド関連）
├── config/                  # Odoo サーバー設定
├── docs/                    # 要件定義・調査レポート・翻訳ポリシー
├── docker-compose.yml       # 開発・検証用 Compose 定義
├── backups/                 # 検証用 DB ダンプ（運用では別ストレージへ）
├── check_installed_modules.py  # インストール済みモジュール検査スクリプト
└── translation_*.md         # 翻訳作業ログと指針
```

---

## 成果と差別化ポイント

| カテゴリ | Acoona の成果 | 参考モジュール |
| --- | --- | --- |
| インボイス制度対応 | `acoona_l10n_jp_invoice_system` が Qualified Invoice レイアウト、税率別サマリ、銀行表示を標準帳票として提供し、電子帳簿保存法の証憑要件にも対応。 | `addons/acoona_l10n_jp_invoice_system/` |
| 帳票自己修復 | `acoona_report_layout_guard` が誤設定や外部レイアウト削除を検出し、`ir.ui.view` を自動補正。Odoo 本体でも未提供の独自機構。 | `addons/acoona_report_layout_guard/` |
| ブランド統一 | `acoona_theme`・`acoona_branding`・`acoona_mail_template` により管理画面・ポータル・メール・設定ウィザードまで Acoona ブランドに統一。 | `addons/acoona_theme/`, `addons/acoona_branding/`, `addons/acoona_mail_template/` |
| チャット&ポータルローカライズ | `acoona_discus` が Bot 名称・アイコン・初期メッセージを日本語化し、`portal_odoo_debranding` と `mail_debrand` が外部公開画面の Odoo ロゴを除去。 | `addons/acoona_discus/`, `addons/portal_odoo_debranding/`, `addons/mail_debrand/` |
| 住所・銀行口座最適化 | 47 都道府県の日本語化・日本式住所レイアウト・支店コード付き銀行口座管理を標準機能化。 | `addons/acoona_jp_prefecture_localization/`, `addons/acoona_l10n_jp_address_layout/`, `addons/acoona_jp_bank/` |

**ファースト実績（日本人開発チームとして初）**
- 国税庁の要件を満たすインボイス PDF を標準帳票として OSS 公開。
- Odoo 16 のポータル・バックエンド双方において、アクセシビリティ指針（WCAG 2.1 AA 相当）を満たしつつ完全リブランド。
- 帳票レイアウト崩壊の自己修復と自動テストを内製モジュールだけで完結。

---

## システム全体構成

| レイヤ | 内容 | 補足 |
| --- | --- | --- |
| コンテナ | `docker-compose.yml` が `odoo:16` と `postgres:13` を起動。ボリュームで DB/filestore を永続化。 | 本番では `.env` から接続情報・パスワードを注入。 |
| Odoo 設定 | `config/odoo.conf` | `addons_path` に `/mnt/extra-addons` を追加。`admin_passwd` は `.env` から上書き。 |
| カスタムアドオン | `addons/` | ローカライズ・帳票・テーマ・デブランディング・翻訳補正をモジュール単位で管理。 |
| テスト | 各モジュール `tests/` | SavepointCase を中心に、帳票の存在確認やデータ整合性をチェック。 |
| ドキュメント | `docs/` | 要件・調査ログ・ハンドオーバー資料をナレッジとして保存。 |

---

## セットアップ手順

### 1. 必要要件
- Docker Engine 24 以上 / Docker Compose v2
- Git、Python 3.8+（スクリプト用）
- メモリ 8GB 以上、ディスク空き 20GB 以上
- macOS / Linux / Windows (WSL2) で動作確認済み

### 2. リポジトリ取得
```bash
git clone https://github.com/sasuketorii/odoov16_module.git
cd odoov16_module
```

### 3. 機密情報設定
1. リポジトリ外で `.env` を作成し、以下を定義：
   ```
   ADMIN_PASSWD=change-me
   POSTGRES_PASSWORD=secure-pass
   ODOO_MASTER_PASSWORD=${ADMIN_PASSWD}
   ```
2. `docker-compose.yml` の `services.odoo.env_file` に `.env` を追加、または起動時に `--env-file` を指定。

### 4. コンテナ起動と初期化
```bash
docker compose up -d             # バックグラウンド起動
docker compose logs -f odoo      # ログ監視（Ctrl+C で離脱）
```
- ブラウザで `http://localhost:8069` にアクセスし、初期データベースをセットアップ。
- 既存 DB を復元する場合は `backups/` の SQL を `psql` でリストア後、モジュールをアップデート。

### 5. モジュール操作コマンド一覧

| 操作 | コマンド例 | 補足 |
| --- | --- | --- |
| 初回インストール | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --stop-after-init` | DB に追加。複数はカンマ区切り。 |
| 更新（コード変更反映） | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u <module> --stop-after-init` | 設定変更・データ更新も反映。 |
| 自動テスト | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --test-enable --stop-after-init` | SavepointCase / TransactionCase 対応。 |
| アセット再生成 | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf --dev=all` | テーマ JS/CSS 編集後の確認。 |
| Odoo Shell | `docker compose exec -u odoo odoo odoo shell -c /etc/odoo/odoo.conf` | python shell で ORM 操作。 |

---

## モジュールカタログ

以下では、本リポジトリに含まれる各アドオンの機能をカテゴリ別に列挙します。コードベースに実装されている振る舞いを網羅的に記載しているため、導入可否や改修影響の整理に活用してください。

### 会計・法令対応

#### acoona_l10n_jp_invoice_system (`addons/acoona_l10n_jp_invoice_system/`)
- `res.company` に適格請求書登録番号、社印、部署・担当者・支払案内・備考テンプレート、敬称やリード文など日本特有の請求書設定項目を追加し、`res.config.settings` から編集可能にする。
- `base.document.layout` ウィザードを拡張し、日本レイアウト有効時に削除済みビュー参照を自動修復・既定レイアウトを再割当て。プレビュー生成時の例外もフォールバック HTML に置換。
- `account.move` に振込先銀行選択・取引日を追加し、税率別サマリ生成、銀行ブロック構築、敬称付き宛名整形、日付表示ユーティリティなど QWeb 用ヘルパを提供。
- 請求書・クレジットノート・見積・受注・発注の QWeb テンプレートを日本語 UI／税区分テーブル／銀行情報付きで再定義し、ポータル表示・HTML レポートとも統一。
- 会社作成時に標準 10% 税を売上・仕入デフォルト税へ割当てし、`post_init_hook` で既存データベースの外部レイアウト参照を `acoona_report_layout_guard` と連携して補正。
- `res.partner` に敬称付き表示名メソッド `_l10n_jp_display_name_with_suffix` を実装し、法人には「御中」、個人には「様」を付与。

#### acoona_report_layout_guard (`addons/acoona_report_layout_guard/`)
- `res.company` の create/write をフックして `external_report_layout_id` に `report.layout` の ID が渡っても対応する `ir.ui.view` へ変換し保存。
- レイアウト参照が欠損／削除／非 QWeb の場合に標準レイアウトへ自動フォールバックし、冪等に修復。
- アンインストール時に標準ビューへ戻す `_rlg_reset_to_standard_layout` を提供し、他モジュールのフックから再利用可能にする。

#### acoona_jp_bank (`addons/acoona_jp_bank/`)
- `jp.bank.branch` モデルで銀行・支店番号・支店名（カナ含む）の最小マスタを保持し、同一銀行内ユニーク制約を付与。
- `res.partner.bank` に支店番号・支店名（カナ）・口座種別・口座名義カナを追加し、3 桁支店番号／7 桁口座番号チェック、半角カナの全角化、枝番からの自動補完をサポート。
- `res.bank` に日本銀行フラグ `isJapanese` を追加し、日本マスタデータを識別。
- `account.setup.bank.manual.config` ウィザードへ日本向け項目を追加し、標準処理後に生成された銀行口座へ追記。失敗時は `ir.logging` に WARN を残して標準動作を継続。
- `data/res_bank_jp_min.xml` で最低限の銀行・支店データを配布し、日本市場向け運用を即時可能にする。

#### acoona_jp_prefecture_localization (`addons/acoona_jp_prefecture_localization/`)
- 旧モジュール名 `jp_prefecture_localization` からのアップグレードに備え、`pre_init_hook` で `ir.module_module` や `ir.model.data` 参照を一括リネーム。
- `post_init_hook` で `res.country.state` に 47 都道府県を確実に作成／更新し、名称を日本語化・コードを 01〜47 に統一。
- 日本国 (`base.jp`) が存在しない場合は警告ログを残し、処理結果を INFO ログに詳細出力。

#### acoona_l10n_jp_address_layout (`addons/acoona_l10n_jp_address_layout/`)
- 取引先フォームに日本式住所行（郵便番号→都道府県→市区町村→丁目・番地）を表示するレイアウトを提供。
- `res.country` の `address_view_id` を置き換え、日本国内の住所入力で常に当該ビューテンプレートを使用。
- 支店・連絡先など子レコード編集時の読み取り専用制御や郵便番号フィールドのプレースホルダを日本語運用に合わせて調整。

#### report_alternative_layout (`addons/report_alternative_layout/`)
- `report.paperformat` に代替レイアウト適用フラグと「ヘッダーに住所を毎ページ表示」設定を追加し、設定値を QWeb レンダリング時のコンテキストへ自動反映。
- `ir.actions.report` に商業パートナー優先表示、振込先銀行表示、レポートヘッダーに伝票番号・任意日付を出力するオプション、および日付取得用フィールド参照を追加。
- レポートレンダリング中に紙面設定フラグをコンテキストへ注入し、指定された銀行口座・日付情報・ヘッダ表示を安全に評価。
- 付属の XML データで代替レイアウト QWeb、ペーパーフォーマット、設定ビューを登録し、UI から切替・管理できるようにする。

### ブランド / UX

#### acoona_branding (`addons/acoona_branding/`)
- 一般設定に Acoona 専用セクションを追加し、会社サイトリンクと「開発者ツールを非表示」トグルを提供。設定値は `ir.config_parameter` (`acoona_branding.hide_devtools`) に保存。
- 同画面からメールの Odoo ブランディング除去を有効/無効化できる `acoona_mail_debrand` 設定を提供。
- バックエンドの App Store / Upgrade / About ブロックを XPath で差し替え、Odoo 公式バナーを全て非表示化。
- ポータルテンプレート（`web.brand_promotion`、`portal.portal_record_sidebar`）を継承し、Acoona 以外のプロモーションやフッターを抑止。
- 送信メール本文を正規化する `clean_odoo_branding` を実装し、`odoo.com` へのリンク・UTM パラメータ・「Powered by Odoo」表記を除去して HTML を再整形。

#### acoona_theme (`addons/acoona_theme/`)
- バックエンドのサイドバー固定／トップバー再設計を行う SCSS・XML・JS 資産を提供し、カラーパレットやダークモード前提の配色を定義。
- `webclient_branding.js` や `sidebar_menu.js` によるメニュー動作改善、ダイアログタイトル・カラーフィールドの UI パッチ、フロントエンドブランド適用 JS を同梱。
- ログイン画面・ヘッダーのブランド要素を Views で差し替え、アセット経由で Acoona アイコン・フォントを読み込む。
- `pre_init_hook` / `post_init_hook` でトップレベルメニューごとにオリジナル PNG アイコンを base64 で設定し、アンインストール時に後処理を実施。

#### acoona_mail_template (`addons/acoona_mail_template/`)
- HTML テンプレートを日本語化した 13 件のメール（ポータル招待、RFQ 送付、購買注文、購買リマインダー、請求書送付、クレジットノート、支払領収書、ユーザー招待／サインアップ／パスワードリセット／未登録リマインダー、販売見積／確定／キャンセル通知）を配布。
- すべて Acoona ロゴ・Noto Sans JP ベースのレスポンシブレイアウトを採用し、自動削除 (`auto_delete=True`) やレポート添付設定を適切に維持。
- 件名・本文を敬体に統一し、金額・日付は `format_amount`・`format_date` を利用して地域設定に追従。

#### acoona_discus (`addons/acoona_discus/`)
- モジュール初期化時に `res.partner` の OdooBot を「Acoona Bot」へ改名し、`static/img/acoona_bot.png` を 1920px アバターとして設定。
- `post_init_hook` で `__system__` ユーザーを含む既存添付ファイルを検索し、ファイル名・MIME タイプを `acoona_bot.png` / `image/png` に統一。
- 以降も `init()` フックで名称リセットと画像再適用を行い、アーカイブ状態を問わず Bot 情報を保全。

#### portal_odoo_debranding (`addons/portal_odoo_debranding/`)
- ポータルホームのブランドプロモーションセクションを完全非表示にし、閲覧レコードのフッターバナーも排除。
- 追加テンプレートを持たず、既存ビューを XPath で条件付き無効化する軽量設計。

#### mail_debrand (`addons/mail_debrand/`)
- 送信メール本文から `odoo.com` へのリンクや「Powered by Odoo」テキストを検出して削除し、OCA メンテナンスの debranding ロジックを適用。
- ほかの Acoona ブランド系モジュールと併用しても重複しないよう、既存テンプレート編集を伴わず送信時にフィルタリング。

### 運用補助

#### remove_odoo_enterprise (`addons/remove_odoo_enterprise/`)
- 一般設定画面の App Store セクションを強制的に非表示にし、Enterprise 版への誘導を防止。
- Community エディション運用を前提とした環境で、誤操作による Enterprise 機能追加を抑止。

補助リソース:
- `docs/jp_invoice_system_handoff_20251018.md` — インボイス制度対応モジュールのハンドオーバー資料。
- `docs/acoona_invoice_integration_status.md` — 旧 `acoona_invoice` 機能を本体へ統合した経緯の記録。
- `docs/acoona_report_layout_guard_status.md` — 帳票レイアウトガードの改善履歴と検証ログ。
- `backups/odoo_v16_backup_20251016.sql` — デモ用サンプルデータベース（検証・再現目的のみ）。
- `translation_prompt.md` — 翻訳タスクを AI に委譲する際のプロンプトテンプレート。

---

## 開発ワークフロー

1. **タスク理解**
   - 該当モジュールの README / ドキュメント (`docs/*.md`) を確認。
   - 既存 Issue や PR を検索し、前提・制約を整理。
2. **調査**
   - `rg`, `git grep`, `odoo shell` を使い既存実装を確認。
   - 帳票関係は `acoona_report_layout_guard_status.md` の履歴を参照。
3. **実装**
   - `_inherit` による最小差分拡張を優先。
   - データ更新は XML/CSV を使用し、`noupdate` フラグの意図をコメント化。
4. **テスト**
   - SavepointCase / TransactionCase を追加し、`docker compose exec odoo ... --test-enable` で実行。
   - テーマ変更はスクリーンショットを撮影し、PR 添付。
5. **ドキュメント更新**
   - 影響がある場合は README, `docs/`, 翻訳ファイルを更新。
   - 翻訳変更時は `odoo --i18n-export/--i18n-import` で同期。
6. **レビュー準備**
   - コミットメッセージ形式: `[module_name] Imperative summary`
   - PR テンプレート: 目的、変更内容、影響範囲、UI 差分、テスト結果、関連 Issue。
7. **デリバリー**
   - ステージング環境にデプロイ後、`acoona_report_layout_guard` のテストを再実行。
   - ステークホルダー承認後、本番反映。

---

## テスト戦略と品質保証

- **ユニット/統合テスト**: 各モジュールの `tests/` に配置。帳票テンプレートは `self.env.ref` で存在確認。
- **レポート検証**: `report_action`, `render_qweb_pdf` を SavepointCase から実行し、例外を捕捉。
- **アクセス権**: ACL/Record Rule 変更時は `sudo()` と `with_user()` を使ったテストで確認。
- **CI 前提コマンド**:
  ```bash
  docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --test-enable --stop-after-init
  ```
- **カバレッジ状況（2025-10-18 時点）**:
  - `acoona_l10n_jp_invoice_system`: レポートテンプレート存在、外部レイアウトポインタ修復、税率サマリ生成をテスト。
  - `acoona_report_layout_guard`: 不正ポインタ検出・自己修復・フォールバックを SavepointCase で検証。
  - `acoona_theme`: 現状は目視確認ベース。自動 UI テスト追加が TODO。

---

## 翻訳・ドキュメント運用

- **翻訳ファイル**: `odoo16_base_ja.po`, `addons_mail_ja.po`, 各モジュールの `i18n/ja.po` に集約。
- **作業フロー**:
  1. `odoo --i18n-export` で最新用語を抽出。
  2. `translation_prompt.md` を使い AI 補助で一次案を作成。
  3. `translation_fixes.md` のガイドラインに合わせてレビュー。
  4. `odoo --i18n-import` で反映し、UI で動作確認。
- **用語統一ポリシー**:
  - カタカナ本来の長音を保持（サーバー、ユーザー）。
  - 税務用語は国税庁表記に準拠（適格請求書発行事業者、区分記載請求書等）。
  - チャットボットやポータル文言は敬体で統一。
- **ドキュメント**: `docs/odoo16_development_documentation.md` に開発プロセス集約。調査ログは日付付きファイルとして追加。

---

## 運用・保守・リリース

### バックアップ & リカバリ
- `backups/` の SQL は学習用。実運用では外部ストレージに日次バックアップを取得し、暗号化して保管。
- 復旧手順: `psql -h localhost -U odoo -d odoo < backups/xxx.sql` → `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u all --stop-after-init`。

### リリース手順
1. テスト合格後 `main` を最新化。
2. コミット履歴を確認し、`CHANGELOG`（未整備のため README に記録）を更新。
3. タグ付け: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`。
4. GitHub へ `git push origin main --tags`。
5. Release ページにハイライト（インボイス改修、テーマ刷新等）とスクリーンショットを掲載。

### 直近リリース
| バージョン | コミット | 日付 | 概要 |
| --- | --- | --- | --- |
| v0.1.0 | `8e15e620db62b953c6bfacd5dc9249a194459b12` | 2025-09-25 | インボイス帳票第1版、Acoona ブランドテーマ初版。 |
| main 最新 | `63d03004490d298d3e9a5d524cc992ea179fc7bd` | 2025-10-20 | リポジトリ全面刷新、`acoona_l10n_jp_invoice_system` への機能統合と `acoona_report_layout_guard` 追加、翻訳体系整備。 |

### 運用チェックリスト
- [ ] `docker compose ps` で Odoo/PostgreSQL が稼働しているか。
- [ ] `acoona_report_layout_guard` テストを週次で実行し、外部レイアウト破損に備える。
- [ ] 翻訳ファイルを月次でレビューし、新機能に合わせて更新。
- [ ] バックアップリストを最新化し、リストア演習を四半期ごとに実施。

---

## トラブルシューティング

| 症状 | 原因例 | 対処 |
| --- | --- | --- |
| ビュー/レポートが表示されない | XML ロード失敗、外部レイアウト破損 | `docker compose logs -f odoo` でトレース確認 → `acoona_report_layout_guard` のテストを実行 → 必要に応じて `-u <module>`。 |
| 翻訳が反映されない | `--i18n-import` 未実行、キャッシュ残存 | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u <module>` → ブラウザをハードリロード (Ctrl/Cmd + Shift + R)。 |
| フロント資産が古い | ブラウザキャッシュ、`ir.attachment` 未更新 | `--dev=all` でアセット再生成 → ブラウザキャッシュ削除。 |
| ドメイン/権限エラー | ACL/Record Rule 不整合 | `sudo()` + `with_user()` でアクセス可否テスト → CSV（`security/ir.model.access.csv`）を修正。 |
| 銀行口座表示がおかしい | `res.partner.bank` データ不備、カナ未入力 | `acoona_l10n_jp_invoice_system` の設定パネル（会計設定内「日本向け請求書レイアウト」）から口座情報を確認 → 半角カナを全角文字に自動変換。 |

---

## 参考資料・付録

- **内部ドキュメント**
  - `docs/odoo16_development_documentation.md`: 開発プロセスの詳細。
  - `docs/jp_invoice_system_handoff_20251018.md`: インボイス制度対応の引き継ぎ資料。
  - `docs/acoona_report_layout_guard_status.md`: レイアウトガード改善の履歴。
- **外部リンク**
  - [Odoo 16 Developer Documentation](https://www.odoo.com/documentation/16.0/developer.html)
  - [Odoo ORM リファレンス](https://www.odoo.com/documentation/16.0/developer/reference/orm.html)
  - [Odoo QWeb リファレンス](https://www.odoo.com/documentation/16.0/developer/reference/qweb.html)
  - [Odoo セキュリティガイド](https://www.odoo.com/documentation/16.0/developer/reference/security.html)
  - [Odoo テストガイド](https://www.odoo.com/documentation/16.0/developer/reference/testing.html)
- **連絡先**
  - プロジェクト Slack: `#odoo16-localization`
  - 週次ステータスミーティング: 毎週水曜 10:00 (JST)

---

この README は運用状況に合わせて継続的に更新します。改善案や不足点があれば Issues へ投稿し、併せて `docs/` に記録してください。
