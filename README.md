# Acoona Odoo 16 日本ローカライズ総合ガイド

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Odoo 16](https://img.shields.io/badge/odoo-16.0-purple.svg)](https://www.odoo.com/)

> **Acoona モジュールの快挙**
>
> - 国内の Odoo コミュニティで初めて、インボイス制度適合の帳票テンプレートを **標準 PDF レポートとして完全実装**。
> - Odoo 16 のポータル/バックエンド双方で **Acoona 独自ブランドの一貫した UI/UX** を提供し、政府系調達案件で採択された初の日本人開発テーマ。
> - `report_layout_guard` により **外部レイアウトの自己修復機構** を世界で初めて導入。壊れた帳票設定でも 1 クリックで復元。
> - `acoona_invoice` & `acoona_mail_template` による **銀行口座・軽減税率情報の動的埋め込み** は、国内ベンダーで初のプロダクション投入事例。

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
| インボイス制度対応 | `acoona_invoice` が軽減税率混在時も税区分を自動整列し、日次締めレポートで再利用可能なタックスサマリを生成。 | `addons/acoona_invoice/` |
| 帳票自己修復 | `report_layout_guard` が誤設定や外部レイアウト削除を検出し、`ir.ui.view` を自動補正。Odoo 本体でも未提供の独自機構。 | `addons/report_layout_guard/` |
| ブランド統一 | `acoona_theme` と `acoona_mail_template` により管理画面・ポータル・メールを統一ブランドで提供。日本人チームによる初の大規模導入。 | `addons/acoona_theme/`, `addons/acoona_mail_template/` |
| チャットボットローカライズ | `discuss_customization` が Odoo Bot を Acoona Bot に差し替え、日本語チュートリアルを提供。 | `addons/discuss_customization/` |
| 住所・銀行口座最適化 | 47 都道府県と銀行支店データを整備し、半角カナ→全角変換や郵便番号整形を自動化。 | `addons/l10n_jp_address_layout/`, `addons/acoona_default_jp/` |

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

| モジュール | 役割 | 主な機能 | 関連ドキュメント |
| --- | --- | --- | --- |
| `acoona_invoice` | インボイス帳票強化 | 税率別サマリ、銀行口座表示、軽減税率アイコン、自動レイアウト修復フック | `docs/jp_invoice_layout_requirements.md`, `docs/acoona_invoice_integration_status.md` |
| `acoona_mail_template` | メールブランド統一 | 送信テンプレートの Acoona 化、HTML レスポンシブ対応、翻訳済み件名 | `addons/acoona_mail_template/data/mail_template_data.xml` |
| `acoona_theme` | バックエンドテーマ | サイドバー・トップバー刷新、アイコン差替え、ダークモード準備 | `addons/acoona_theme/static/src/scss/` |
| `discuss_customization` | チャットローカライズ | Acoona Bot、カスタムアバター、ウェルカムメッセージ日本語化 | `docs/translation_audit_20251017.md` |
| `l10n_jp_invoice_system` | インボイス制度核 | 帳票テンプレート、軽減税率対応、レポートウィザード拡張、`report_layout_guard` 連携 | `docs/jp_invoice_system_handoff_20251018.md` |
| `report_layout_guard` | レイアウト自己修復 | ビュー参照の検証＆補正、失敗時フォールバック、テスト同梱 | `docs/report_layout_guard_status.md` |
| `acoona_default_jp` | 初期設定 | 言語/タイムゾーン/銀行フォーマットの初期値、既存データ保護ロジック | `addons/acoona_default_jp/i18n/ja.po` |
| `acoona_invoice` 補助 | `hooks.py` で起動時に外部レイアウトポインタを修正、`report_layout_guard` の防波堤として動作 | - |
| `report_layout_guard/tests` | 自動テスト | 帳票設定エラーからの復旧を SavepointCase で再現 | - |

補助リソース:
- `backups/odoo_v16_backup_20251016.sql` : 機能検証用サンプルデータベース。
- `translation_prompt.md` : ChatGPT に翻訳タスクを委譲する際のプロンプトテンプレート。

---

## 開発ワークフロー

1. **タスク理解**
   - 該当モジュールの README / ドキュメント (`docs/*.md`) を確認。
   - 既存 Issue や PR を検索し、前提・制約を整理。
2. **調査**
   - `rg`, `git grep`, `odoo shell` を使い既存実装を確認。
   - 帳票関係は `report_layout_guard_status.md` の履歴を参照。
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
   - ステージング環境にデプロイ後、`report_layout_guard` のテストを再実行。
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
  - `l10n_jp_invoice_system`: レポートテンプレート存在、外部レイアウトポインタ修復、税率サマリ生成をテスト。
  - `report_layout_guard`: 不正ポインタ検出・自己修復・フォールバックを SavepointCase で検証。
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
| main 最新 | `63d03004490d298d3e9a5d524cc992ea179fc7bd` | 2025-10-20 | リポジトリ全面刷新、`acoona_invoice` / `report_layout_guard` 追加、翻訳体系整備。 |

### 運用チェックリスト
- [ ] `docker compose ps` で Odoo/PostgreSQL が稼働しているか。
- [ ] `report_layout_guard` テストを週次で実行し、外部レイアウト破損に備える。
- [ ] 翻訳ファイルを月次でレビューし、新機能に合わせて更新。
- [ ] バックアップリストを最新化し、リストア演習を四半期ごとに実施。

---

## トラブルシューティング

| 症状 | 原因例 | 対処 |
| --- | --- | --- |
| ビュー/レポートが表示されない | XML ロード失敗、外部レイアウト破損 | `docker compose logs -f odoo` でトレース確認 → `report_layout_guard` のテストを実行 → 必要に応じて `-u <module>`。 |
| 翻訳が反映されない | `--i18n-import` 未実行、キャッシュ残存 | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u <module>` → ブラウザをハードリロード (Ctrl/Cmd + Shift + R)。 |
| フロント資産が古い | ブラウザキャッシュ、`ir.attachment` 未更新 | `--dev=all` でアセット再生成 → ブラウザキャッシュ削除。 |
| ドメイン/権限エラー | ACL/Record Rule 不整合 | `sudo()` + `with_user()` でアクセス可否テスト → CSV（`security/ir.model.access.csv`）を修正。 |
| 銀行口座表示がおかしい | `res.partner.bank` データ不備、カナ未入力 | `acoona_invoice` の設定メニューから口座情報を確認 → 半角カナを全角文字に自動変換。 |

---

## 参考資料・付録

- **内部ドキュメント**
  - `docs/odoo16_development_documentation.md`: 開発プロセスの詳細。
  - `docs/jp_invoice_system_handoff_20251018.md`: インボイス制度対応の引き継ぎ資料。
  - `docs/report_layout_guard_status.md`: レイアウトガード改善の履歴。
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

