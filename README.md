# Odoo 16 日本ローカライズ開発ハンドブック

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Odoo 16](https://img.shields.io/badge/odoo-16.0-purple.svg)](https://www.odoo.com/)

日本市場向けに Odoo 16 をローカライズするためのモジュール群と運用ノウハウを集約したリポジトリです。本書は新規参加者が環境構築からデリバリーまで迷わず進められるよう、アーキテクチャ、モジュール構成、開発手順、ドキュメント索引をまとめた実務向けガイドです。

---

## 1. プロジェクト概要
- **目的**: 日本の商慣習・法令（インボイス制度、銀行口座仕様、住所表記等）に準拠した Odoo 16 モジュールを提供し、ワンストップで運用可能にする。
- **スコープ**: カスタマイズはすべて `addons/` 配下のモジュールとして実装し、Odoo コアには手を加えない。Docker Compose を前提に動作確認を行う。
- **対象読者**: 日本ローカライズを担当する Odoo 開発者・QA・テクニカルライター。

### 1.1 アーキテクチャ方針
- Docker 上で **odoo(16.0)** + **PostgreSQL 13** を起動し、`/mnt/extra-addons` に本リポジトリのモジュールをマウントするシンプル構成。
- 帳票レイアウト・翻訳・テーマ改修など横断的な変更は、専用モジュールとフックで疎結合化。
- 文書化とテストを重視し、主要モジュールには SavepointCase ベースの自動テストを同梱。

---

## 2. システム構成
| レイヤ | 内容 | 補足 |
| --- | --- | --- |
| コンテナ | `docker-compose.yml` が `odoo:16` と `postgres:13` を定義。ボリュームでデータ永続化。 | 初回起動時に構成ファイルとモジュールをマウント。 |
| アプリ設定 | `config/odoo.conf` | `addons_path` に `/mnt/extra-addons` を追加。管理者パスワードは `admin_passwd = sasuketorii`（初期値として同梱。運用環境では `.env` 経由で上書き必須）。 |
| カスタムアドオン | `addons/` | 日本固有機能・テーマ・デブランディングモジュール。依存関係はマニフェストで管理。 |
| ドキュメント | `docs/` | 要件定義や調査レポート、翻訳ポリシーなどの実務資料。 |
| スクリプト | `install_module.py` ほか | Docker 内からモジュールのインストール／アンインストールを自動化。 |
| 翻訳 | `odoo16_base_ja.po` | コミュニティ訳をベースに長音記号など日本語表記を精査・補正。 |

---

## 3. セットアップ手順

### 3.1 前提条件
- Docker Engine 24+ / Docker Compose v2
- Git, Python 3.8+（メンテナンス用スクリプト向け）
- 8GB 以上のメモリを推奨（PDF レポート生成で余裕を持たせる）

### 3.2 リポジトリ取得
```bash
git clone https://github.com/sasuketorii/odoov16_module.git
cd odoov16_module
```

### 3.3 機密情報の管理
1. `.env` をリポジトリ外で作成し、DB パスワードや管理者パスワードを定義。
2. `docker-compose.yml` で `env_file: [.env]` を追加するか、起動時に `--env-file` を指定。

例:
```
ADMIN_PASSWD=change-me
POSTGRES_PASSWORD=secure-pass
ODOO_MASTER_PASSWORD=${ADMIN_PASSWD}
```

### 3.4 コンテナ起動と初期化
```bash
# 初回起動
docker compose up -d

# ログ確認（エラー調査時）
docker compose logs -f odoo
```
- ブラウザで `http://localhost:8069` にアクセス。初期ユーザーは `admin / admin`（稼働環境では直ちに変更）。
- モジュールインストールは次節のコマンド例を参照。

### 3.5 よく使う Docker コマンド
| 用途 | コマンド | 備考 |
| --- | --- | --- |
| 起動 / 停止 | `docker compose up -d` / `docker compose stop` | 初回はイメージ取得待ち。 |
| ログ監視 | `docker compose logs -f odoo` | エラー時はトレースを記録。 |
| モジュール初回導入 | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --stop-after-init` | データベースへインストール。 |
| モジュール更新 | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u <module> --stop-after-init` | コード変更反映。 |
| テスト実行 | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --test-enable --stop-after-init` | TransactionCase / SavepointCase に対応。 |
| アセット再生成 | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf --dev=all` | CSS/JS を変更した際の調査に利用。 |

---

## 4. リポジトリ構成
```
.
├── addons/                  # 日本ローカライズ関連モジュール
├── config/odoo.conf         # Odoo サーバー設定
├── docs/                    # 要件定義・調査ノート
├── docker-compose.yml       # コンテナ定義
├── install_module.py        # モジュール導入スクリプト
├── uninstall_module.py      # モジュール削除スクリプト
├── check_installed_modules.py # ブランディング系モジュール監査
├── odoo16_base_ja.po        # カスタム日本語翻訳
├── translation_fixes.md     # 翻訳改善リスト
└── README.md                # 本ドキュメント
```

### 4.1 キーディレクトリの補足
- **addons/**: 1 モジュール = 1 ディレクトリ。`models/`, `views/`, `data/`, `i18n/`, `tests/` を標準構成とする。
- **docs/**: 要件・調査の一次情報。`invoice_要件定義.md` や `report_layout_guard_status.md` など、開発判断の根拠を保管。
- **config/**: 環境依存値を `.env` で上書きする前提で、共有しても問題ない設定のみ格納。
- **翻訳関連**: `odoo16_base_ja.po` は Odoo コア翻訳の修正。差分と手順は `translation_fixes.md`・`translation_prompt.md` に記載。

---

## 5. モジュールカタログ
主要モジュールをカテゴリ別に整理しました。依存関係はマニフェスト参照、テスト有無は `tests/` ディレクトリで確認できます。

### 5.1 コアローカライズ
| モジュール | 主な機能 | 依存 | 備考 |
| --- | --- | --- | --- |
| `l10n_jp_invoice_system` | 日本向け請求書レイアウト「Japan」の提供、会社設定フィールド拡張、Document Layout ウィザード補正、銀行口座表示、登録番号検証。 | `web`, `base`, `base_setup`, `account` | `tests/test_views_load.py` でテンプレート／レイアウトポインタの回帰テストを実施。Acoona Invoice 機能を統合済み。 |
| `jp_bank_account_minimal` | 日本の銀行口座項目（支店番号、口座種類、名義カナ等）とカナ自動変換、マスタ最小セット。 | `base`, `contacts`, `web`, `account` | 7桁口座番号・全角カナ検証を実装。銀行・支店コード初期データを提供。 |
| `l10n_jp_address_layout` | QWeb 外部レイアウトで日本住所を縦書き風に整形。 | `web` | `<t>` テンプレート内で郵便番号・都道府県・市区町村を連結。 |
| `acoona_jp_prefecture_localization` | `res.country.state` を日本語表記 + JIS コードに統一。 | `base` | README 同梱。インストール時に既存データを日本語へ上書き。 |
| `acoona_default_jp` | デフォルト言語を `ja_JP`、通貨を `JPY` に設定。会社通貨の自動更新を安全に実行。 | `base`, `base_setup`, `account` | 設定ウィザードから変更可能。仕訳のある会社は通貨更新をスキップ。 |

### 5.2 UI / ブランディング
| モジュール | 主な機能 | 依存 | 備考 |
| --- | --- | --- | --- |
| `acoona_theme` | 固定サイドバー・トップバー刷新・ログイン画面刷新を含むバックエンドテーマ。 | `base`, `web`, `mail` | hooks でインストール前後の初期化処理あり。`static/src/` に SCSS/JS。 |
| `sasuke_backend_theme2` | `acoona_theme` のベースとなったテーマの改定版。 | `base`, `web`, `mail` | レガシー検証用として併存。ベーステーマ比較に利用。 |
| `acoona_branding2` | 設定画面に Acoona ブランディングと開発者モード切替を追加。メール送信フッターから Odoo ブランドを排除。 | `base_setup`, `portal`, `mail` | メール本文レンダリングをパッチ。 |
| `mail_debrand` | 送信メールの「Powered by Odoo」を除去。 | `mail` | 長文テンプレートにも対応するよう 20 文字超の `odoo` を除去。 |
| `portal_odoo_debranding` | ポータルサイトの Odoo ブランドを削除。 | `portal` | フロントエンドのヘッダ・フッタを置換。 |
| `remove_odoo_enterprise` | Enterprise モジュールの痕跡と設定項目を非表示。 | `base_setup` | SavepointCase テスト付。アンインストールで標準設定に戻る。 |
| `discuss_customization` | OdooBot を「Acoona Bot」に改名。 | `mail` | チャット UI の細かな文言調整。 |

### 5.3 帳票補助 / 共通基盤
| モジュール | 主な機能 | 依存 | 備考 |
| --- | --- | --- | --- |
| `report_layout_guard` | `res.company.external_report_layout_id` を常に `ir.ui.view` に正規化。 | `base`, `web` | `tests/test_guard.py` で report.layout → view 変換と自己修復を検証。 |
| `report_alternative_layout` | 複数帳票レイアウトの候補を拡張、Paperformat 追加。 | `web` | レイアウト切替 UI の拡張と紙面設定調整。 |
| `acoona_mail_template` | 日本語ローカライズ済みメールテンプレート群。 | `base`, `mail`, `sale`, `purchase`, `account`, `portal` | `data/mail_template_data.xml` にビジネス文書テンプレート。 |
| `acoona_invoice` | 旧日本向け請求書モジュール。 | `account`, `l10n_jp_invoice_system` | 機能は `l10n_jp_invoice_system` に統合済み。参照用に保管し、新規開発では使用しない。 |

---

## 6. 主要機能の詳細

### 6.1 `l10n_jp_invoice_system`
- **Document Layout 拡張**: `report.layout` に「Japan」を追加し、`base.document.layout` ウィザードで既定選択できるように `_ensure_japan_layout` と `default_get` を強化。
- **会社設定フィールド**: 登録番号、社印、銀行口座デフォルト、支払案内、請求先敬称など日本固有項目を `res.company` に追加し、`res.config.settings` から編集可能に提供。
- **銀行口座ブロック**: 請求書 PDF に振込先情報（銀行名・支店・口座種別・名義）を表示し、複数口座時はリスト展開。
- **税率別集計**: `_get_jp_tax_summary` で `tax_totals` から税率毎の小計を抽出し、日本式の「税率区分」「消費税」「金額（税抜）」表を生成。
- **軽減税率表示**: 明細行に軽減税率対象の場合「※」を付与。複数税率が混在する場合も `tax_ids` から自動判定。
- **レイアウト自己修復**: `_acoona_invoice_fix_external_layout_pointer` が古い `report.layout` ID を `ir.ui.view` へ置換し、`report_layout_guard` と併用して不整合を防止。
- **テスト**: SavepointCase により外部レイアウトテンプレートの存在確認／ポインタ修復／税率キー生成を継続的に検証。

### 6.2 銀行口座モジュール
- `jp_bank_account_minimal` が `res.partner.bank` に支店番号・口座種類（普通/当座/貯蓄など）・名義カナを追加し、半角カナ入力を全角に正規化。
- `account_setup_bank_manual_config` を継承してウィザード UI を日本語化し、銀行支店マスタ（必要最小限）を `data/res_bank_jp_min.xml` で配布。

### 6.3 住所・郵便
- `acoona_jp_prefecture_localization` が 47 都道府県の名称とコードを日本語に統一。インストール時に既存データを更新。
- `l10n_jp_address_layout` が帳票内の住所を「〒」＋都道府県＋市区町村＋丁目・番地の順で整形。

### 6.4 レポートレイアウトガード
- `report_layout_guard` は `res.company.write/create` をフックし、外部レイアウトが常に `ir.ui.view` を参照するよう変換。壊れた参照は標準 `web.external_layout_standard` にフォールバック。
- `docs/report_layout_guard_status.md` に調査ログと修正の経緯を記録。

### 6.5 デフォルト設定・ブランド統一
- `acoona_default_jp` でデフォルト言語/通貨を管理。既存仕訳がある会社には通貨変更を適用しない安全策を実装。
- `acoona_branding2`, `mail_debrand`, `portal_odoo_debranding`, `remove_odoo_enterprise` で UI／メール／ポータルから Odoo ブランドを排除し、Acoona ブランドに統一。

---

## 7. 翻訳・言語ポリシー
- **翻訳ファイル**: `odoo16_base_ja.po` をベースに、長音記号の欠落や日本語として不自然な用語を修正。作業方針は `translation_fixes.md` と `translation_prompt.md` に詳細を記載。
- **メンテナンス手順**: `pip install polib` などでツール環境を整え、`odoo --i18n-export/--i18n-import` で PO ファイルを同期。大量置換前にはバックアップを作成。
- **レビュー基準**: 用語統一（例: ユーザー、サーバー、仕入）と敬体の簡潔さ（「〜できます」）を徹底。

---

## 8. 開発ワークフロー（推奨）
1. **タスク理解**: `docs/` と対象モジュール README を確認し、要件と制約を把握。
2. **事前調査**: `rg` や Odoo shell で既存実装を確認。レイアウト関連は `report_layout_guard_status.md` を参照。
3. **実装**: `_inherit` を活用して最小限の差分で拡張。依存モジュールは `__manifest__.py` で明示。
4. **テスト**: SavepointCase / TransactionCase を追加し、`docker compose exec odoo ... --test-enable` で回帰を保護。
5. **ドキュメント更新**: 影響がある場合は `README.md`, `docs/`, 翻訳ファイルを更新。
6. **レビュー準備**: コミットメッセージ形式 `[module_name] Imperative summary`、PR には目的・変更内容・影響範囲・スクリーンショット・テスト結果を添付。

---

## 9. テストと品質保証
- **ユニット / 結合テスト**: `tests/test_*.py` を各モジュールに配置。帳票読み込みは `self.env.ref(...)` で存在確認。
- **レポート検証**: `report_action` や `render_qweb_pdf` を SavepointCase から呼び出し、例外発生を防止。
- **アクセス制御**: ACL 変更時は `sudo()` を併用したテストで権限を確認。
- **CI 前提コマンド**:
  ```bash
  docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --test-enable --stop-after-init
  ```
- **カバレッジ状況（2025-10-14 時点）**:
  - `l10n_jp_invoice_system`: テンプレート存在、レイアウトポインタ、銀行口座 fallback を検証。
  - `report_layout_guard`: レイアウト→ビュー変換と自己修復の単体テスト。
  - `remove_odoo_enterprise`: 設定項目の可視性テスト（詳細はモジュール内参照）。
  - その他: テーマ・テンプレート系は視覚確認を前提とし、スクリーンショットを PR に添付。

---

## 10. スクリプト & 自動化ツール
| スクリプト | 用途 | 使い方 |
| --- | --- | --- |
| `install_module.py` | Docker コンテナ内で指定モジュールをインストール。既定は `acoona_jp_prefecture_localization`。 | `docker compose exec odoo python3 /mnt/extra-addons/install_module.py <module_name>` |
| `uninstall_module.py` | モジュールをアンインストール。DB 名は引数 2 で指定可能。 | `docker compose exec odoo python3 /mnt/extra-addons/uninstall_module.py <module_name> [db]` |
| `check_installed_modules.py` | OdooRPC を利用してブランディング関連モジュールのインストール状況を一覧表示。 | ホスト側で `pip install odoorpc` 後、`python3 check_installed_modules.py` |

---

## 11. ドキュメント索引
| ファイル | 概要 |
| --- | --- |
| `docs/invoice_要件定義.md` | インボイス制度対応請求書の完全仕様（グラフィック・データマッピング・テスト項目）。 |
| `docs/jp_invoice_layout_requirements.md` | PDF レイアウトの色・寸法・QWeb 実装ポイントを整理。 |
| `docs/acoona_invoice_integration_status.md` | 旧 `acoona_invoice` から新モジュールへの統合作業ログと既知課題。 |
| `docs/report_layout_guard_status.md` | レイアウト参照不整合の調査レポートと対応履歴。 |
| `docs/report01.md` | Document Layout ウィザード拡張の調査メモ。 |
| `docs/odoo16_development_documentation.md` | 公式ドキュメントリンク集。 |

---

## 12. トラブルシューティング
- **請求書 PDF が標準レイアウトに戻る**: `l10n_jp_invoice_system` を再インストール後、`report_layout_guard` が有効か確認。`_acoona_invoice_fix_external_layout_pointer()` を Odoo shell から実行。
- **翻訳が反映されない**: `--i18n-export` / `--i18n-import` を実行し、`.po` の差分を確認。必要に応じて `-u <module>` でモジュール更新。
- **テーマ変更が反映されない**: `docker compose exec odoo odoo -c /etc/odoo/odoo.conf --dev=all` でアセット再生成し、ブラウザでハードリロード（Cmd/Ctrl + Shift + R）。
- **銀行口座エラー**: 口座番号は必ず 7 桁、名義は全角カナで入力。`jp_bank_account_minimal` の制約を参照。
- **Document Layout ウィザードの候補不足**: `report.layout` レコードが存在するかを `odoo shell` で確認し、`report_layout_guard` / `l10n_jp_invoice_system` の hooks を再評価。

---

## 13. ロードマップ / 今後の予定
- **祝日カレンダー**: 日本の法定休日を自動反映するモジュールを検討中。
- **和暦対応**: 請求書やレポートで元号表示を切替可能にする仕組みを設計中。
- **住所検索**: 郵便番号 → 住所自動補完を提供するウィジェット構想。
- **翻訳強化**: `translation_fixes.md` の優先度順に PO ファイルを改善。

---

## 14. コントリビューションポリシー
- コミットメッセージは `[module_name] Imperative summary` 形式。
- PR には目的・背景、変更内容、影響範囲、UI 変更のスクリーンショット、テスト結果、関連 Issue を必ず記載。
- 新しい設定項目や運用フローを追加した場合は、README もしくは該当モジュールの README、`docs/` を更新。
- 翻訳追加時は、キーを英語・日本語の両方で確認し、冗長表現を避ける。

---

## 15. ライセンス・サポート
- すべてのモジュールは **LGPL-3** ライセンスで公開。
- 企業サポートや拡張相談は **REV-C inc.**（https://company.rev-c.com）まで。
- バグや改善提案は GitHub Issue へ。調査ログは `docs/` に追記して共有。

---

本 README は 2025-10-14 時点の情報を基準としています。更新や課題があれば `docs/` ディレクトリおよび本書を随時改訂してください。
