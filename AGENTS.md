# Odoo16 日本向けローカライズ開発ガイド

このリポジトリは Odoo 16 の日本ローカライズモジュールを開発・運用するための作業場所です。新しく参加したエージェント（LLM/開発者）が迷わずにモジュール開発を完走できるよう、環境準備からデリバリーまでのルールを以下にまとめます。

---

## 1. プロジェクト全体像
- **目的**: 日本の商習慣・法令（インボイス制度、銀行口座、住所表記など）に準拠した Odoo 16 モジュールを提供する。
- **範囲**: すべてのカスタマイズは `addons/` 配下のモジュールとして実装し、Odoo コアファイルは変更しない。
- **想定利用環境**: Docker Compose で Odoo + PostgreSQL を起動し、ブラウザから http://localhost:8069 にアクセスして検証する。

---

## 2. 環境と基本コマンド
| フェーズ | コマンド/手順 | メモ |
| --- | --- | --- |
| 起動/停止 | `docker compose up -d` / `docker compose stop` | 初回起動時はイメージ取得を待つ。 |
| ログ監視 | `docker compose logs -f odoo` | エラーの確認に必須。 |
| モジュール初回導入 | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --stop-after-init` | DB へインストール。 |
| モジュール更新 | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u <module> --stop-after-init` | コード変更後の反映。 |
| テスト実行 | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --test-enable --stop-after-init` | TransactionCase / SavepointCase でテスト。 |
| アセット再生成 | `docker compose exec odoo odoo -c /etc/odoo/odoo.conf --dev=all` | CSS/JS 変更時のデバッグに有効。 |

環境変数や資格情報は `.env` で渡し、リポジトリへコミットしません。

---

## 3. 典型的な開発フロー
1. **タスク理解**: 関連ドキュメントは `docs/` および対象モジュールの README を確認。  
2. **調査**: `rg`, `git grep`, `odoo shell` などで既存実装を把握する。  
3. **実装**: `_inherit` を優先し、必要最小限の依存でモジュールを拡張。  
4. **テスト**: 単体/統合テストを実行し、回帰の有無を確認。  
5. **ドキュメント更新**: README や要件定義、翻訳ファイルなど関連ドキュメントを更新。  
6. **レビュー準備**: コミットメッセージと差分を整え、影響範囲・確認手順をまとめる。

---

## 4. ディレクトリとモジュール構成

```
addons/
└── module_name/
    ├── __manifest__.py
    ├── __init__.py
    ├── models/
    ├── views/
    ├── security/
    │   └── ir.model.access.csv
    ├── data/
    ├── i18n/
    │   └── ja.po
    ├── static/
    │   ├── src/js/
    │   ├── src/scss/
    │   └── description/
    └── tests/
        └── test_*.py
```

- モジュール名は `snake_case`。新規モデルは `_name = 'x_module.model'` 形式で命名。
- `__manifest__.py` の `depends` は最小限とし、`assets` 更新時はパス漏れに注意。
- セキュリティ定義 (`ir.model.access.csv`) と翻訳 (`i18n/ja.po`) を必ず整備。

---

## 5. コーディング規約
### Python
- Python 3.8+ / 4 スペースインデント。`.editorconfig` を遵守。
- `api.depends`, `api.constrains`, `api.model` を適切に利用し副作用を最小化。
- ロギングは `_logger` 経由。`print` やコメントアウトコードは残さない。
- データ整形・日本語処理（カナ変換等）は専用ヘルパー/ユーティリティに切り出す。

### XML/QWeb
- ビュー継承は `record id="..."` + `<xpath>` で最小差分を心掛ける。
- `t-translation="off"` を不要に使わず、翻訳可能なテキストは `_()` や `t-esc` を用いる。
- テンプレート内の日付・金額は `format_date`, `format_amount` 等のユーティリティを利用。

### JavaScript / SCSS
- 主要 JS は `static/src/js/`、スタイルは `static/src/scss/` に配置。
- OWL/サービスパッチ時は競合を避けるため `registry.category` を正しく操作。
- SCSS はトークン (`$color-primary` など) を定義し、`@import` 順序を `tokens → base → components` とする。
- **住所フォームのレイアウト注意:** `l10n_jp_address_layout` が生成する住所行は `.o_address_format` 配下に `street`, `state_id`, `city` などを縦に並べます。テーマ側で横並びを調整する際は、以下のガイドラインに従いフォーム幅の変動（固定サイドバーなど）でも破綻しないようにすること。
  1. `.o_address_state` / `.o_address_city` の幅を 50% にする場合は、既存の `margin-right: 2%` を明示的に打ち消すか、`display:flex` + `gap` で余白を制御する。中途半端に幅だけ上書きすると合計幅が 100% を超え、フィールドが重なる。
  2. クラスのない既存構造にも対応できるよう、テーマでは `div:has(> .o_address_state)` のように継承された DOM を検知してまとめて制御する。新しいラッパークラス（`o_address_state_city_row`）を導入した場合は両方にスタイルを適用する。
  3. SCSS 変更後は必ず `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u acoona_theme --stop-after-init`（ならびに関連テーマ）でアセットを再生成し、ブラウザ側でもハードリロードして確認する。

### データ・翻訳
- XML データファイルは `noupdate` フラグを目的に応じて設定。
- 翻訳文字列は `i18n/ja.po` に集約し、`odoo --i18n-export`/`--i18n-import` コマンドで同期。
- データ更新で過去情報を上書きする場合はバックアップ手順を README 等に記載。

---

## 6. テスト戦略
- **ユニット/統合テスト**: `tests/test_*.py` で `TransactionCase` または `SavepointCase` を使用。  
- **ビュー読み込みテスト**: `self.env.ref("module.view_id")` を `assertTrue` で確認。  
- **アクセス権検証**: ACL/Record Rule に変更がある場合は `sudo` 切替でアクセス可否をテスト。  
- **レポート/QWeb**: `report_action` や `render_qweb_pdf` を用いて例外が発生しないことを確認。  
- **CI 前提**: `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --test-enable --stop-after-init`
  を実行し、エラーなしで完走させる。

---

## 7. コミット・レビュー・ドキュメント
- コミットメッセージ形式: `[module_name] Imperative summary`（例: `[l10n_jp_invoice_system] Fix external layout pointer`）。
- PR には以下を含める: 目的・背景、変更内容、影響範囲、UI 変更のスクリーンショット、テスト結果、関連 Issue。
- README や要件定義 (`docs/`) に影響がある場合は漏れなく更新。
- モジュールの利用手順や既知の制約は該当モジュールの README に追記。

---

## 8. エージェント運用ポリシー（Codex CLI）
- 応答言語は日本語。英語ログには日本語で補足説明を付ける。
- シェルコマンド実行前に「何をするか」を日本語で 1–2 文記述してから実行する。
- 複数工程のタスクでは `update_plan` ツールを使用し、常に 1 項目のみ `in_progress` とする。
- ネットワークアクセスは必要最小限。外部情報を引用する際は出典を明示。
- 機密情報（パスワード等）は環境変数で扱い、リポジトリへ保存しない。

---

## 9. トラブルシューティングのヒント
- **ビュー/レポートが表示されない**: `docker compose logs -f odoo` でトレースバック確認 → 対応する XML をチェック。
- **翻訳が反映されない**: `--i18n-export` → `--i18n-import` で PO を再生成、もしくは `-u <module>` で更新。
- **フロント資産が古い**: ブラウザのハードリロード (Ctrl/Cmd + Shift + R) と `--dev=all` の利用。
- **ドメインや権限エラー**: ACL/Record Rule を再確認し、`sudo()` で想定アクセス範囲を検証。

---

## 10. 参考資料
- 内部まとめ: `docs/odoo16_development_documentation.md`
- Odoo 16 Developer Documentation: https://www.odoo.com/documentation/16.0/developer.html
- ORM リファレンス: https://www.odoo.com/documentation/16.0/developer/reference/orm.html
- QWeb リファレンス: https://www.odoo.com/documentation/16.0/developer/reference/qweb.html
- セキュリティガイド: https://www.odoo.com/documentation/16.0/developer/reference/security.html
- テストガイド: https://www.odoo.com/documentation/16.0/developer/reference/testing.html

---

このガイドの内容はモジュール開発の進展に応じて更新します。運用上の課題や改善案があれば `docs/` へ記録し、AGENTS.md に反映してください。
