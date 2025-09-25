# タスク完了時のチェックリスト

- 影響モジュールのテスト実行: `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --test-enable --stop-after-init`。
- 機能反映（更新）: `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u <module> --stop-after-init` 後に `docker compose up -d` で再起動。
- 翻訳の更新/確認: `i18n/ja.po` を同期、UI の日本語表示を目視確認。
- アクセス権/セキュリティ確認: 権限で意図通りに見える/操作できるか。
- ログ確認: `docker compose logs -f odoo` にトレースバックが無いこと。
- ドキュメント更新: `README.md` や `docs/` に必要な追記があれば更新。
- コミット/PR: 規約に沿ったメッセージと PR 本文（目的/範囲/スクショ/テスト計画/関連 Issue）。
- 依存関係: 新規依存は最小限かつ妥当か（他モジュールへの影響を評価）。
