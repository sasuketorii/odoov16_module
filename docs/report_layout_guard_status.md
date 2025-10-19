# レイアウト選択不整合 調査レポート（2025-10-13）

## 対象環境
- モジュール: `l10n_jp_invoice_system`（installed） + `report_layout_guard`（installed）
- Odoo 16.0-20250725 / PostgreSQL (Docker compose)
- 調査対象会社: `My Company`（ID: 1）

## 直近の挙動
- 管理設定 → ドキュメントレイアウト画面で「Japan」を選択して保存しても、システム設定では `external_layout_striped` が表示・適用される。
- 請求書PDFおよびプレビューも標準ストライプレイアウトのまま。

## 事実関係
1. `report.layout` レコード一覧（`odoo shell` より抜粋）  
   - `Light` (ID=2, sequence=2, view=202, key=`web.external_layout_standard`)  
   - `Boxed` (ID=3, sequence=3, view=200, key=`web.external_layout_boxed`)  
   - `Bold` (ID=4, sequence=4, view=201, key=`web.external_layout_bold`)  
   - `Striped` (ID=1, sequence=5, view=199, key=`web.external_layout_striped`)  
   - `Japan` (ID=37→実行のたびに再生成, sequence=6, view=1079, key=`l10n_jp_invoice_system.external_layout_jp`)
2. `res.company` (`My Company`) の現在値  
   - `acoona_invoice_use_jp_layout = True`  
   - `external_report_layout_id = ir.ui.view(199)` ⇒ `web.external_layout_striped`
3. ドキュメントレイアウトウィザード (`base.document.layout`) で `default_get()` を呼んだ結果  
   - `report_layout_id` フィールドは `False` のまま返却され、ラジオボタンの初期選択は Striped となる。  
   - ログ出力: `JP layout default_get: fields=... company=1 layout=None` ※`company.external_report_layout_id` が日本レイアウトでも、`report.layout` レコードはセットされない。  
4. `report_layout_guard` のガード  
   - `company.write({'external_report_layout_id': report_layout_japan.id})` を実行すると 1079 (Japan) に正しく変換される。  
   - しかしドキュメントレイアウトウィザードを再度開くと `report_layout_id` が空で、保存後に Striped へ逆戻り。  
   - ログでも `company external view` がウィザード後に 199 に戻る様子が観測される。

## 原因候補
1. `base.document.layout` の保存ロジック（標準実装）が `report_layout_id` の値をもとに `company.external_report_layout_id` を上書きするが、フォーム初期化時に `report_layout_id` が空のため「デフォルト1番目（Striped）」が自動的に選択され、そのまま会社設定に書き戻されている可能性が高い。  
2. `report.layout` レコードがモジュールアップグレード時に消えて再生成される（ログに“Deleting ... report_layout_japan”）ため、`res.company.acoona_invoice_previous_layout_id` が切り替えをトリガし、ガード以前のロジックで Striped を再適用している可能性もある。

## これまでに実施した修正
- `base_document_layout.default_get()` に会社の外部レイアウトビューから `report.layout` を逆引きし、初期値としてセットするロジックを追加。  
  しかし実際の環境では `report_layout_id` が `False` のままであり、追加ロジックが動作していない（要再現調査）。
- `report_layout_guard` で `external_report_layout_id` を常に `ir.ui.view` に正規化し、ログで監視できるようにした。

## 追加調査が必要なポイント
1. ウィザードの初期化時に `company.external_report_layout_id` を参照する他のカスタムコードが存在するか（`report_layout_guard` 以外）。  
2. `report.layout` レコードがアップグレード時に再生成されるたび、`res.company.external_report_layout_id` が現在のビュー ID と整合しているか。現在は `report.layout` の ID が毎回変化しており、過去に保存された `acoona_invoice_previous_layout_id` が無効になっている可能性がある。  
3. フロントエンド側（Document Layout フォーム）の JavaScript が `report_layout_id` を強制的に初期化していないか（標準コードでは単純に初期レコードを1件取得するだけだが、カスタムモジュールが影響している可能性）。  
4. `account.report_invoice_document` 系テンプレートに対する継承衝突（日本版と標準の継承順）の確認。請求書 PDF が標準に戻る原因の一部と考えられる。

## 推奨アクション
1. `base.document.layout` の保存時（`write()`/`save()`）で `report_layout_id` に値が入っているかをログする。  
2. `res.company.write()` が `acoona_invoice_previous_layout_id` とフラグの切替で Striped に戻していないか再度確認（`report_layout_guard` と `l10n_jp_invoice_system` 両方のログを突き合わせる）。  
3. 必要に応じて、Document Layout フォームの初期値を強制するパッチを検討（`action_open` やコンテキストに `default_report_layout_id` をセットする等）。  
4. PDF テンプレートの崩れ調査用に、現在ロードされている QWeb テンプレート一覧を抜粋して確認する（`ir.ui.view` の継承順や `priority` を含む）。

## 添付情報
- `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo_v16 -u l10n_jp_invoice_system --stop-after-init` の実行ログ：report_layout_japan が毎回削除→再生成されていることを示す。
- `odoo shell` で `company.write({'external_report_layout_id': report_layout.id})` → `company.external_report_layout_id.id == 1079` になることを確認済み。
- ウィザード生成直後のログ：`JP layout default_get: ... final report_layout_id=38` が出力されるが、フォーム実際の初期表示は Striped のまま。

## 調査アップデート（2025-10-13 20:42 JST）
- `addons/l10n_jp_invoice_system/models/base_document_layout.py` の `_compute_preview` が、レイアウトが存在する場合でも `else` 分岐で `external_report_layout_id` を標準ストライプに上書きしていた。
- 上記条件を「レイアウトが未設定または削除されている場合のみ補正する」よう修正。`missing_layout = not company.external_report_layout_id or not company.external_report_layout_id.exists()` を導入し、Japan レイアウト使用時は `external_layout_jp`、それ以外は既存のデフォルトレイアウトを設定するよう限定。
- `odoo shell` でウィザードを新規作成した際、会社の `external_report_layout_id` が 1086 (`l10n_jp_invoice_system.external_layout_jp`) のまま変化しないことを確認（以前はウィザード作成直後に 199 へ戻っていた）。
- ブラウザ UI での保存検証、および `SavepointCase` ベースの再発防止テスト追加は今後のタスクとして検討。

---
本レポートは 2025-10-13 18:16（JST）時点の状況を整理したものです。さらに調査や修正が必要な場合は、本ファイルを更新してください。
