# sasuke_backend_theme3 v3 移行手順

本ドキュメントは、旧版 (v2 系派生) から v3 へ切替える際に発生し得るキャッシュやデータ残存を解消するための手順です。

## 1. 事前確認
- バックアップ: Odoo DB と filestore をバックアップする (`docker compose exec db pg_dump ...`)。
- サービス停止: メンテナンス時間帯に `docker compose stop odoo` で停止。

## 2. キャッシュ・モジュール情報のリセット
1. `addons/sasuke_backend_theme3/__pycache__` を削除済みなので、追加で `docker compose exec odoo find /tmp -name "*.pyc" -delete` を実行。
2. Odoo を再起動 (`docker compose up -d odoo`) し、新しいマニフェストを読み込ませる。

## 3. 旧データ参照の確認
Odoo コンテナ内でシェルを起動し、以下を実行して旧 XML ファイルを参照するレコードが残っていないか確認します。

```bash
docker compose exec odoo odoo shell -d <DB_NAME>
```

```python
from odoo import api, SUPERUSER_ID
from pprint import pprint

env = api.Environment(env.cr, SUPERUSER_ID, {})
model_data = env['ir.model.data'].search([
    ('module', '=', 'sasuke_backend_theme3'),
    ('name', 'like', 'webclient_templates%')
])
pprint(model_data.read(['name', 'model', 'res_id']))
```

- 結果が空であれば旧パス参照はありません。
- 残っている場合は `model_data.unlink()` で削除し、後続でモジュールを更新します。

## 4. モジュール再インストール
1. `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u sasuke_backend_theme3 --stop-after-init`
2. ログにエラーがないことを確認。
3. 必要に応じてブラウザ側で「開発者モード → アセットを再読み込み」。

## 5. 動作確認
- バックエンドにログインし、サイドバーが常時表示されること、幅の縮小/モバイルでのトグル動作を確認。
- 代表画面（会計/販売/ディスカッション等）の表示崩れがないことをチェック。

## 6. トラブルシュート
- 再インストール時に `File not found: sasuke_backend_theme3/views/webclient_templates.xml` が発生した場合: バージョン 3 のファイル構成が正しく配備されているか、`docker compose exec odoo ls /mnt/extra-addons/sasuke_backend_theme3/views` で確認。
- それでも解決しない場合は、`ir.module.module` の `state` を `uninstalled` にしてから再度 `-i` を実行。

