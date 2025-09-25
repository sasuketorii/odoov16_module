# よく使うコマンド（開発）

- サービス起動: `docker compose up -d`
- ログ追跡: `docker compose logs -f odoo`
- 初回インストール: `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --stop-after-init`
- 既存モジュール更新: `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u <module> --stop-after-init`
- テスト実行: `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -i <module> --test-enable --stop-after-init`

## リポジトリ操作（Darwin/macOS）
- 変更確認: `git status` / 差分: `git diff`
- 高速検索: `rg <pattern>`（未導入なら `brew install ripgrep`）
- ファイル一覧: `ls -la`、ツリー表示: `tree -L 2`（`brew install tree`）

## Odoo 運用ヒント
- モジュール識別子はディレクトリ名（例: `addons/jp_prefecture_localization` → `<module>=jp_prefecture_localization`）。
- インストール/更新は `--stop-after-init` を付けて一度プロセスを停止→`docker compose up -d` で再起動。
