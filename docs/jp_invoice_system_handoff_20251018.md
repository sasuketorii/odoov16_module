# l10n_jp_invoice_system 引き継ぎメモ（2025-10-18）

## 対応概要
- フォームレイアウトの統一  
  - `account.move`・`sale.order`・`purchase.order` の左右カラム幅を揃えるため、ビューに独自クラスを付与し、`static/src/scss/account_move_form.scss` を拡張。  
  - 請求書・見積もりフォームのタイトル行はフル幅、ドロップダウンやテキストフィールドは `flex` で100%幅になるよう調整。
- 日時入力の分単位統一  
  - フォーム側：`sale_order_views.xml` / `purchase_order_datetime_views.xml` に `options="{ 'format': 'YYYY-MM-DD HH:mm', 'datetimepicker': {'format': 'YYYY-MM-DD HH:mm', 'useSeconds': false} }"` を設定。  
  - モデル側：`sale.order`・`purchase.order` の `create` / `write` で秒未満をゼロ化するヘルパを追加。  
  - 既存データは `date_trunc('minute', …)` で補正済み。
- 購買関連レポートの日時フォーマット  
  - `report_purchasequotation_document` を拡張し、納入予定日を `YYYY年MM月DD日 HH:mm` で表示。既にあった購買注文書レポート拡張と分けて同ファイルに併載。
- その他  
  - `__manifest__.py` に追加SCSS（`web.assets_backend`）・新ビューXMLを登録。
  - `purchase_order_views.xml` にタイトル・カラム用のクラスを付与。

## 作業履歴（主要コマンド）
- モジュール再読込  
  - `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo_v16 -u l10n_jp_invoice_system --stop-after-init`
- 既存日時の補正  
  - `docker compose exec -e PGPASSWORD=odoo odoo psql -h db -U odoo -d odoo_v16 -c "UPDATE purchase_order SET date_order = date_trunc('minute', date_order), date_planned = date_trunc('minute', date_planned);"`
  - `docker compose exec -e PGPASSWORD=odoo odoo psql -h db -U odoo -d odoo_v16 -c "UPDATE sale_order SET date_order = date_trunc('minute', date_order);"`

## 確認済みポイント
- 販売見積／請求書／購買見積フォームで左右端・プレースホルダーが揃うこと。  
- 購買見積PDFの「納入予定日」が `YYYY年MM月DD日 HH:mm` 表記で出力され、秒表示が消えていること。  
- 既存レコードを更新・再保存しても秒が復活しないこと。

## 留意事項・残課題
- OWL/JS 側の datetimepicker は `useSeconds: false` 指定で対応したが、他モジュールで秒を必要とするケースがある場合はコンテキストオプションの競合に注意。  
- 既存データ補正は実行済みだが、外部連携で秒付きの値が再投入される場合は同様に丸める処理が必要。  
- レポート等で独自フォーマットが必要な箇所があれば、`format_datetime` を用いたテンプレート拡張を追加で検討する。

## 参考ファイル
- `addons/l10n_jp_invoice_system/views/account_move_views.xml`  
- `addons/l10n_jp_invoice_system/views/purchase_order_views.xml`  
- `addons/l10n_jp_invoice_system/views/sale_order_views.xml`  
- `addons/l10n_jp_invoice_system/views/purchase_order_datetime_views.xml`  
- `addons/l10n_jp_invoice_system/views/report_purchaseorder_document_jp.xml`  
- `addons/l10n_jp_invoice_system/models/sale_order.py`  
- `addons/l10n_jp_invoice_system/models/purchase_order.py`  
- `addons/l10n_jp_invoice_system/static/src/scss/account_move_form.scss`

