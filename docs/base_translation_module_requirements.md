# Odoo16 日本語翻訳モジュール要件定義書

- 文書番号: TR-REQ-001  
- バージョン: 0.2 (2025-10-24 改訂)  
- 改訂者: Codex (LLM エージェント)  
- 対象システム: Odoo 16 日本向け環境 (Docker Compose 運用)  

## 1. 背景・目的

Odoo 16 の標準 UI/メッセージおよび社内テーマ (`acoona_theme`) 固定文言を、日本語翻訳モジュールのインストールだけで確実に切り替えられる仕組みを整備する。  
「モジュール導入＝翻訳適用完了」とすることで、`--i18n-import` や手動補正を不要にし、担当者や環境が変わっても翻訳品質を維持できることを目的とする。

## 2. 範囲

- **対象モジュール**
  - 新規作成: `acoona_l10n_base_translations`（仮称）
  - 翻訳対象 Odoo コア: `base`
  - 必須依存: `acoona_theme`, `purchase`（および今後翻訳を束ねる標準/カスタムモジュール）
- **対象環境**: 当リポジトリの Docker Compose 構成 (`docker compose up -d` で起動する開発・ステージング・本番環境)。
- **対象 DB**: 日本向け標準テンプレート DB（テナント問わず共通の翻訳を適用する）。

### 2.1 スコープ内要素

- `odoo16_base_ja.po` の翻訳文字列をモジュール配下の `i18n/ja_JP.csv` に統合し、自動インポートを実現する。
- `acoona_theme` 固定表示テキスト（例: `MENU`）の翻訳を同モジュールで提供。
- Odoo 標準モジュール（例: `purchase`）で JSON フィールドに保存されるメニュー名など、PO だけでは反映されにくい文言をデータ更新でカバーする。
- モジュールインストール／更新時に翻訳・データが確実に適用されるフックの導入。
- 翻訳更新ワークフロー（エクスポート→差分確認→再インポート）の定義。
- 翻訳導入後の確認項目・テスト項目の明文化。

### 2.2 スコープ外要素

- テーマ自体の構造変更や UI レイアウト調整。
- 本要件書で指定していない追加モジュールの翻訳整備（必要になった際は要件書を改訂する）。
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
2. `i18n/ja_JP.csv` に統合された `odoo16_base_ja.po` およびテーマ・標準モジュール固有文字列  
3. JSON フィールド上の文言を日本語化するためのデータ更新ファイル（例: `data/ir_ui_menu_translation.xml`）  
4. 翻訳更新手順書（README または `docs/` 内補足資料）  
5. テスト記録（翻訳適用確認チェックリスト）  
6. リリースノート（翻訳差分と対応日）  

## 5. 前提条件・制約

- Docker Compose を利用した Odoo 16 環境が稼働していること。
- 翻訳ファイル `odoo16_base_ja.po` は UTF-8 エンコーディングで提供されること。
- ターゲット言語 `ja_JP` (必要に応じて `ja`) が Odoo 上にインストール済みであること。
- 翻訳適用は Odoo の標準翻訳仕組みに準拠し、手動 SQL 更新は行わない（自動データ更新は XML/CSV で提供）。
- 翻訳更新時はリポジトリに `.po` 差分をコミットし、履歴管理する。
- 開発ガイドライン（`docs/odoo16_development_documentation.md`）を遵守する。

## 6. 要件詳細

### 6.1 機能要件

| ID | 要件 | 詳細 |
| --- | --- | --- |
| F-01 | 翻訳モジュール構成 | `addons` 配下に新規モジュールを作成し、`__manifest__.py` に `depends: ['base', 'acoona_theme', 'purchase']` を最低限指定する。翻訳以外の Python モデルは追加しないが、フックやデータ更新を配置できる構造にする。 |
| F-02 | 翻訳ファイル配置 | `i18n/ja_JP.csv` を作成し、`odoo16_base_ja.po` の内容と社内カスタム文言を統合する。CSV のヘッダー (`module,type,name,res_id,src,value,comments`) を維持し、UTF-8 で保存する。 |
| F-03 | テーマ文言翻訳 | `acoona_theme` 固定文言（例: `addons/acoona_theme/static/src/xml/top_bar.xml` の `MENU`）を `i18n/ja_JP.csv` に追加し、日本語/英語 UI の双方で破綻しないよう管理する。 |
| F-04 | 標準モジュール翻訳網羅 | `purchase` など社内利用が確定している標準モジュールの主要ラベル（アプリ名、メニュー、ボタン）をリストアップし、欠落分は `i18n/ja_JP.csv` に追記する。対象一覧は README に明記する。 |
| F-05 | 自動読み込みフック | `post_init_hook` を実装し、インストール/更新時に `trans_load` (overwrite=True) で `i18n/ja_JP.csv` を読み込む。対象言語コードは `ja_JP`（必要に応じて `ja`）を自動判定し、未インストールの場合はエラーログを出す。 |
| F-06 | JSON フィールド/メニュー対応 | PO で反映されない JSON フィールド（例: `ir_ui_menu.name`）は XML データ（`data/ir_ui_menu_translation.xml` 等）で `ir.translation` または `ir.ui.menu` を更新し、「購買 ▶ 仕入」等の上書きを保証する。更新は `noupdate="0"` で登録し、モジュール更新時にも反映されるようにする。 |
| F-07 | 手順一貫性 | モジュールのインストール／更新だけで翻訳が適用されること。README には「`--i18n-import` や JSON の直接投入は不要・禁止」である旨を明記する。 |
| F-08 | 更新手順 | 翻訳更新時は `odoo --i18n-export` で英語原文を取得し差分確認 → `ja_JP.csv` 更新 → フック挙動確認 → PR という手順を README に定義し、レビューチェックリストに含める。 |
| F-09 | 既存翻訳維持 | 既存環境で個別に登録された翻訳を削除しない。必要に応じて `noupdate="1"` や `overwrite=False` で上書き抑止できる構成とし、影響箇所を要件書に記録する。 |
| F-10 | ランタイム動作 | 翻訳適用後、ユーザーが UI 言語を日本語に変更すると当該文言が即時反映されること。特にアプリスイッチャー／トップバーの表示確認を受入基準に含める。 |

### 6.2 非機能要件

- **保守性**: 翻訳ファイルの更新履歴が追跡可能であること。行数が大きいため、差分レビューを容易にするためにセクション単位でコミットを分割することを推奨。
- **可搬性**: どの環境でも `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u acoona_l10n_base_translations --stop-after-init` の一回で適用できること。追加 CLI や JSON インポート手順を要求しない。
- **信頼性**: フック実行に失敗した場合はログに WARNING 以上を出力し、モジュール更新を失敗させる。QA がログ検査で失敗を検知できること。
- **品質**: 機械翻訳不可。`odoo16_base_ja.po` 提供元の翻訳品質を維持し、社内用語修正が必要な場合はレビュープロセスを設ける。
- **セキュリティ**: 翻訳ファイルに機密情報（社内固有 ID 等）を含めない。

### 6.3 データ要件

- `i18n/ja_JP.csv` の `src` は Odoo 英語テキストと一致させる。
- `odoo16_base_ja.po` 由来の `msgctxt` やコメントに相当する情報は `comments` 列で保持し、メタ情報（翻訳者、更新日時）は別途ドキュメントに記載する。
- テーマ固有翻訳は `#. module: acoona_theme` のコメントを追加し、将来の抽出時に対象を識別できるようにする。
- メニュー等の JSON フィールド更新は、`ir.translation` 用 XML/CSV データ、もしくは `ir.ui.menu` レコード更新で管理し、対象レコード ID を要件書と README に明記する。
- 特殊文字（全角スペース、制御文字）は使用しない。必要に応じて HTML エスケープ (`&amp;` など) を利用する。

### 6.4 運用・保守要件

- 翻訳ファイル更新時は、`docs/translation_audit_YYYYMMDD.md` に差分概要・レビュワー・適用日時を記録する。
- リリース前には QA が日本語 UI の主要画面を確認し、不自然な訳語がある場合は報告する。
- 翻訳に関する問い合わせ窓口（Slack `#odoo-l10n-jp` 等）を明記する。
- モジュールインストール後に `ir.module.module` 状態と `ir_translation` / `ir_ui_menu` の抜き取り確認を実施し、`Purchase` が `仕入` へ切り替わっていることを証跡として残す。

## 7. 開発ポリシー・実装方針

- モジュール命名は `acoona_l10n_base_translations` を暫定とし、最終決定はプロダクトオーナー承認後に行う。
- フォルダ構成は以下を基本とする。

```
addons/acoona_l10n_base_translations/
├── __init__.py
├── __manifest__.py
├── hooks.py
├── data/
│   └── ir_ui_menu_translation.xml   # JSON フィールド上書き等
├── i18n/
│   └── ja_JP.csv                    # 翻訳ファイル
└── README.md                        # 翻訳更新フローと注意点
```

- `__manifest__.py` の主要設定:
  - `depends`: `['base', 'acoona_theme', 'purchase']`
  - `data`: `['data/ir_ui_menu_translation.xml']` など翻訳以外の更新を列挙。
  - `post_init_hook`: `"post_init_hook"` を設定し、翻訳ローダーを起動。
  - `auto_install`: False, `application`: False。バージョン管理は `16.0.1.0.0` 形式で開始し、翻訳更新ごとにサブバージョンを increment。
- 翻訳ファイルの統合は自動化スクリプト（例: `scripts/update_translations.sh`）を別途用意し、Transifex など外部ソースとの差分取得を容易にする（次フェーズ検討）。

## 8. テスト要件

| テスト ID | 内容 | 手順 | 判定基準 |
| --- | --- | --- | --- |
| T-01 | 翻訳モジュールインストール | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i acoona_l10n_base_translations --stop-after-init` | コマンドがエラーなく完了し、`ir.translation` に日本語レコードが生成される。 |
| T-02 | Base モジュール翻訳確認 | 日本語ユーザーでログインし、`設定 > ユーザーと会社 > ユーザー` などで UI 文言を確認。 | `MENU` など対象文言が適切な訳で表示される。 |
| T-03 | 購買メニュー翻訳確認 | `ir.ui.menu` を SQL または Odoo シェルで参照し、`purchase.menu_purchase_root` の `name->>'ja_JP'` を確認。 | `Purchase` が `仕入` に置き換わっている。 |
| T-04 | テーマ翻訳確認 | トップバー（PC/SP）で `MENU`、`Apps` 等の表示を確認。 | 英語 UI では英語、日本語 UI では日本語が表示される。 |
| T-05 | 更新テスト | 翻訳ファイルを更新後 `-u` 実行。 | 既存レコードが重複せず更新される。ログに警告・エラーがない。 |
| T-06 | 回帰テスト | 最低限の機能回帰（ログイン、アプリ切替、テーマ切替）を実施。 | 翻訳導入による機能不具合が発生しない。 |

テスト結果は QA が `docs/translation_test_report_YYYYMMDD.md` に記録する。

## 9. リスクと対策

| リスク | 影響 | 対策 |
| --- | --- | --- |
| 翻訳ファイルの巨大差分でレビュー困難 | レビュー遅延 | 翻訳更新時はセクション単位でコミット分割し、差分サマリーを添付する。 |
| テーマ翻訳とコア翻訳で重複キーが発生 | 想定外表示 | `module` コメントと `msgctxt` を維持し、どのモジュールの翻訳か識別できるよう管理する。 |
| 翻訳更新が本番適用されない | 利用者体験低下 | リリースフローに `-u acoona_l10n_base_translations` 実行を必須ステップとして追加し、リリースチェックリストに明記する。 |
| Odoo バージョンアップで原文変化 | 翻訳欠落 | 半期ごとに `odoo --i18n-export` を実行し、欠落サマリをレビューする。 |
| JSON フィールド更新が反映されない | アプリ名が英語に戻る | `data/ir_ui_menu_translation.xml` を `noupdate="0"` で管理し、モジュール更新テスト（T-03）を必須化する。 |
| フック実行失敗に気付かない | 翻訳が全体的に未適用 | ログ監視手順を定義し、`post_init_hook` 内で失敗時に `UserError` を投げてトランザクションをロールバックする。 |

## 10. 導入手順 (参考)

1. ブランチ作成: `git checkout -b feature/base-translation-module`
2. モジュール骨組み作成（`__init__.py`, `__manifest__.py`, `hooks.py`, `data/`, `i18n/`, `static/description/`）。
3. `odoo16_base_ja.po` を `i18n/ja_JP.csv` に統合し、不足する社内文言・標準モジュール文言を追加。
4. `data/ir_ui_menu_translation.xml` を作成し、`Purchase` など JSON ベースの表示名を上書きする。
5. `post_init_hook` を実装し、対象言語に対して `trans_load(..., overwrite=True)` を実行する。
6. README に翻訳適用フローと禁止事項（手動インポート禁止）を記載。
7. `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i acoona_l10n_base_translations --stop-after-init` を実行し、ログでフック成功を確認。
8. テスト項目 T-01〜T-06 を実施し、結果を `docs/translation_test_report_YYYYMMDD.md` に記録。
9. PR 作成 (`[acoona_l10n_base_translations] Ensure JP translations auto-load` 形式)。
10. QA 承認後、リリースチェックリストに沿って本番へ適用。

## 11. オープン課題・検討事項

1. モジュール名の最終決定 (`acoona_l10n_base_translations` で問題ないか要確認)  
2. `odoo16_base_ja.po` の更新頻度と取得元の公開手順（Transifex 連携 or 定期同期）  
3. テーマ以外の翻訳要望（将来的に他テーマやブランドへの展開予定有無）  
4. 翻訳レビュー体制（誰が訳語を変更できるか、承認フローの定義）  
5. JSON フィールド更新対象の拡張可否（追加メニュー、ボタン）と管理方法  
6. 既存環境に個別上書き翻訳がある場合の移行手順（CSV エクスポート→再インポートの要否）  

## 12. 参考資料

- `odoo16_base_ja.po` （本リポジトリ直下）
- `addons/acoona_theme/static/src/xml/top_bar.xml`
- `/usr/lib/python3/dist-packages/odoo/addons/purchase/i18n/ja.po`（翻訳元参照用）
- Odoo 標準 DB 内 `ir_ui_menu` テーブル
- `docs/odoo16_development_documentation.md`
- Odoo 公式ドキュメント: https://www.odoo.com/documentation/16.0/developer/reference/i18n.html

---

本要件定義書に基づき、詳細設計・実装フェーズへ進む前に利害関係者のレビュー承認を取得すること。
