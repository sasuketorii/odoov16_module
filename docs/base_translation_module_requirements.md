# Odoo16 日本語翻訳モジュール要件定義書

- 文書番号: TR-REQ-001  
- バージョン: 0.1 (2025-10-23 作成)  
- 作成者: Codex (LLM エージェント)  
- 対象システム: Odoo 16 日本向け環境 (Docker Compose 運用)  

## 1. 背景・目的

Odoo 16 の標準 UI/メッセージを日本語化するために `odoo16_base_ja.po` を導入しつつ、社内テーマ (`acoona_theme`) の固定文言も同一フローで適用できるモジュールを整備する。翻訳の適用手順をモジュール化することで、環境差や作業者の手順漏れを防止し、継続的な翻訳更新を容易にすることを目的とする。

## 2. 範囲

- **対象モジュール**
  - 新規作成: `acoona_l10n_base_translations`（仮称）
  - 既存テーマ: `acoona_theme`
  - 翻訳対象 Odoo コア: `base`
- **対象環境**: 当リポジトリの Docker Compose 構成 (`docker compose up -d` で起動する開発・ステージング・本番環境)。
- **対象 DB**: 日本向け標準テンプレート DB（テナント問わず共通の翻訳を適用する）。

### 2.1 スコープ内要素

- `odoo16_base_ja.po` の翻訳文字列をモジュール配下の `i18n/ja.po` として組み込み、自動インポートを実現する。
- `addons/acoona_theme/static/src/xml/top_bar.xml` に含まれる固定表示テキスト（例: `MENU`）の翻訳を同モジュールで提供。
- 翻訳更新ワークフロー（エクスポート→差分確認→再インポート）の定義。
- 翻訳導入後の確認項目・テスト項目の明文化。

### 2.2 スコープ外要素

- テーマ自体の構造変更や UI レイアウト調整。
- 翻訳対象外モジュール（Sales、Accounting など個別モジュール）の翻訳整備。
- 翻訳以外の日本ローカライズ機能要件（帳票、税制対応等）。

## 3. 利害関係者

| 役割 | 氏名/部署 | 責務 |
| --- | --- | --- |
| プロダクトオーナー | Acoona PM | 翻訳適用範囲・品質の承認 |
| 開発リーダー | 日本ローカライズ Tech Lead | 実装レビュー、開発工数調整 |
| 開発担当者 | Odoo ローカライズ開発チーム | モジュール実装・テスト |
| QA | QA チーム | 翻訳適用確認、回帰テスト |
| 運用 | インフラ/CS | 本番への導入計画とリリース判定 |

## 4. 成果物

1. `addons/acoona_l10n_base_translations/` (仮称) 以下に配置された翻訳モジュール一式  
2. `i18n/ja.po` に統合された `odoo16_base_ja.po` およびテーマ固有文字列  
3. 翻訳更新手順書（README または `docs/` 内補足資料）  
4. テスト記録（翻訳適用確認チェックリスト）  
5. リリースノート（翻訳差分と対応日）  

## 5. 前提条件・制約

- Docker Compose を利用した Odoo 16 環境が稼働していること。
- 翻訳ファイル `odoo16_base_ja.po` は UTF-8 エンコーディングで提供されること。
- 翻訳適用は Odoo の標準翻訳仕組みに準拠し、手動 SQL 更新は行わない。
- 翻訳更新時はリポジトリに `.po` 差分をコミットし、履歴管理する。
- 開発ガイドライン（`docs/odoo16_development_documentation.md`）を遵守する。

## 6. 要件詳細

### 6.1 機能要件

| ID | 要件 | 詳細 |
| --- | --- | --- |
| F-01 | 翻訳モジュール構成 | `addons` 配下に新規モジュールを作成し、`__manifest__.py` に `depends: ['base', 'acoona_theme']` を指定する。翻訳のみを目的とするため Python モデル・ビューは追加しない。 |
| F-02 | 翻訳ファイル配置 | `i18n/ja.po` を作成し、`odoo16_base_ja.po` の内容を統合する。ファイルヘッダーはプロジェクト情報に合わせて更新し、`Project-Id-Version`・`Language` 等を保持する。 |
| F-03 | テーマ文言翻訳 | `acoona_theme` 内の固定文言（`addons/acoona_theme/static/src/xml/top_bar.xml` の `MENU` 等）を `i18n/ja.po` へ追加し、日本語・英語いずれの UI 状況でも適切に表示されるよう翻訳キーを管理する。 |
| F-04 | 翻訳同期 | 翻訳更新時に `odoo --i18n-export` で最新英語原文を取得し、`odoo16_base_ja.po` と差分がある場合は翻訳追加・更新を行う。更新手順を README に記載する。 |
| F-05 | 自動適用 | モジュールのインストール・更新 (`-u`) 時に翻訳が自動インポートされること。追加スクリプトを不要とし、Odoo 標準の翻訳ロード機構を利用する。 |
| F-06 | 既存翻訳維持 | 既存環境で個別に登録された翻訳を削除しない。必要に応じて `noupdate="1"` を利用して、標準更新で上書きされないよう調整する。 |
| F-07 | ランタイム動作 | 翻訳適用後、ユーザーが UI 言語を日本語に変更すると当該文言が即時反映されること。 |

### 6.2 非機能要件

- **保守性**: 翻訳ファイルの更新履歴が追跡可能であること。行数が大きいため、差分レビューを容易にするためにセクション単位でコミットを分割することを推奨。
- **可搬性**: どの環境でも `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u acoona_l10n_base_translations --stop-after-init` の一回で適用できること。
- **品質**: 機械翻訳不可。`odoo16_base_ja.po` 提供元の翻訳品質を維持し、社内用語修正が必要な場合はレビュープロセスを設ける。
- **セキュリティ**: 翻訳ファイルに機密情報（社内固有 ID 等）を含めない。

### 6.3 データ要件

- `i18n/ja.po` の原文 (`msgid`) は Odoo 英語テキストと一致させる。
- `odoo16_base_ja.po` 由来の `msgctxt` やコメントを保持し、メタ情報（翻訳者、更新日時）を更新する。
- テーマ固有翻訳は `#. module: acoona_theme` のコメントを追加し、将来の抽出時に対象を識別できるようにする。
- 特殊文字（全角スペース、制御文字）は使用しない。必要に応じて HTML エスケープ (`&amp;` など) を利用する。

### 6.4 運用・保守要件

- 翻訳ファイル更新時は、`docs/translation_audit_YYYYMMDD.md` に差分概要・レビュワー・適用日時を記録する。
- リリース前には QA が日本語 UI の主要画面を確認し、不自然な訳語がある場合は報告する。
- 翻訳に関する問い合わせ窓口（Slack `#odoo-l10n-jp` 等）を明記する。

## 7. 開発ポリシー・実装方針

- モジュール命名は `acoona_l10n_base_translations` を暫定とし、最終決定はプロダクトオーナー承認後に行う。
- フォルダ構成は以下を基本とする。

```
addons/acoona_l10n_base_translations/
├── __init__.py        # 空ファイル
├── __manifest__.py
├── i18n/
│   └── ja.po          # 翻訳ファイル
└── README.md          # 翻訳更新フローと注意点
```

- `__manifest__.py` の主要設定:
  - `depends`: `['base', 'acoona_theme']`
  - `data`: 空リスト（翻訳のみのため）。`auto_install`: False, `application`: False。
  - バージョン管理: `16.0.1.0.0` 形式で開始し、翻訳更新ごとにサブバージョンを increment。
- 翻訳ファイルの統合は自動化スクリプト（例: `scripts/update_translations.sh`）を別途用意し、Transifex など外部ソースとの差分取得を容易にする（次フェーズ検討）。

## 8. テスト要件

| テスト ID | 内容 | 手順 | 判定基準 |
| --- | --- | --- | --- |
| T-01 | 翻訳モジュールインストール | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i acoona_l10n_base_translations --stop-after-init` | コマンドがエラーなく完了し、`ir.translation` に日本語レコードが生成される。 |
| T-02 | Base モジュール翻訳確認 | Odoo に日本語ユーザーでログインし、`設定 > ユーザーと会社 > ユーザー` などで UI 文言が日本語化されていることを確認。 | `MENU` など対象文言が適切な訳で表示される。 |
| T-03 | テーマ翻訳確認 | `MENU`、`Apps` 等のトップバー表示がローカライズされる。 | 英語 UI では英語のまま、日本語 UI では日本語が表示される。 |
| T-04 | 更新テスト | 翻訳ファイルを更新後 `-u` 実行。 | 既存レコードが重複せず更新される。ログに警告・エラーがない。 |
| T-05 | 回帰テスト | 最低限の機能回帰（ログイン、アプリ切替、テーマ切替）を実施。 | 翻訳導入による機能不具合が発生しない。 |

テスト結果は QA が `docs/translation_test_report_YYYYMMDD.md` に記録する。

## 9. リスクと対策

| リスク | 影響 | 対策 |
| --- | --- | --- |
| 翻訳ファイルの巨大差分でレビュー困難 | レビュー遅延 | 翻訳更新時はセクション単位でコミット分割し、差分サマリーを添付する。 |
| テーマ翻訳とコア翻訳で重複キーが発生 | 想定外表示 | `module` コメントと `msgctxt` を維持し、どのモジュールの翻訳か識別できるよう管理する。 |
| 翻訳更新が本番適用されない | 利用者体験低下 | リリースフローに `-u acoona_l10n_base_translations` 実行を必須ステップとして追加し、リリースチェックリストに明記する。 |
| Odoo バージョンアップで原文変化 | 翻訳欠落 | 半期ごとに `odoo --i18n-export` を実行し、欠落サマリをレビューする。 |

## 10. 導入手順 (参考)

1. ブランチ作成: `git checkout -b feature/base-translation-module`
2. `odoo16_base_ja.po` を `addons/acoona_l10n_base_translations/i18n/ja.po` に配置
3. `__manifest__.py` 作成・設定
4. README に翻訳更新手順を記載
5. `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i acoona_l10n_base_translations --stop-after-init`
6. UI で翻訳確認、テスト実施
7. PR 作成 (`[acoona_l10n_base_translations] Add base translation module` 形式)
8. QA 承認後、リリース手順に従い本番へ適用

## 11. オープン課題・検討事項

1. モジュール名の最終決定 (`acoona_l10n_base_translations` で問題ないか要確認)  
2. `odoo16_base_ja.po` の更新頻度と取得元の公開手順（Transifex 連携 or 定期同期）  
3. テーマ以外の翻訳要望（将来的に他テーマやブランドへの展開予定有無）  
4. 翻訳レビュー体制（誰が訳語を変更できるか、承認フローの定義）  
5. 既存環境に個別上書き翻訳がある場合の移行手順（CSV エクスポート→再インポートの要否）  

## 12. 参考資料

- `odoo16_base_ja.po` （本リポジトリ直下）
- `addons/acoona_theme/static/src/xml/top_bar.xml`
- `docs/odoo16_development_documentation.md`
- Odoo 公式ドキュメント: https://www.odoo.com/documentation/16.0/developer/reference/i18n.html

---

本要件定義書に基づき、詳細設計・実装フェーズへ進む前に利害関係者のレビュー承認を取得すること。
