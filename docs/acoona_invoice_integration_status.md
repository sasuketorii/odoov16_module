# Acoona Invoice 統合作業 現状まとめ

## 概要

`acoona_invoice` モジュールを `l10n_jp_invoice_system` に統合する作業を実施中。日本向け請求書レイアウトの機能を単一モジュールに集約し、依存関係の複雑さを排除することを目的とする。

## 統合作業の進捗

### ✅ 完了した作業

1. **モジュール構造の統合**
   - `acoona_invoice` の機能を `l10n_jp_invoice_system` に統合
   - 依存関係の整理と単一モジュール化

2. **モデル拡張の統合**
   - `res_company.py`: Acoona Invoice の全フィールドを追加
   - `account_move.py`: 日本向けユーティリティ関数を統合
   - `res_config_settings.py`: 設定画面で編集可能なフィールドを統合
   - `base_document_layout.py`: Document Layout ウィザードの修正機能を統合

3. **ビューの統合**
   - `report_invoice_document_acoona.xml`: Acoona の日本向けレイアウトを統合
   - `res_config_settings_views.xml`: Acoona Invoice の設定項目を統合

4. **初期化フックの統合**
   - `hooks.py`: インストール時の自動設定機能を統合

5. **エラー修正**
   - `invoice_payment_ref` → `payment_reference` フィールド名修正
   - `company.fax` フィールド削除（Odoo 16 で廃止）
   - `format_date()` 関数の引数修正

### ❌ 現在発生中の問題

**根本的な問題**: `external_report_layout_id` に `report.layout` のレコード ID が保存され、本来参照すべき `ir.ui.view` と不整合になっている

**エラーメッセージ**:
```
AssertionError: template is required
Template: web.external_layout
Path: /t/t[4]
Node: <t t-if="company.external_report_layout_id" t-call="{{company.external_report_layout_id.sudo().key}}"/>
```

**問題の詳細**:
1. Document Layout ウィザードや請求書メールでレイアウト切り替えを実行
2. 会社に保存されるレイアウト参照が `report.layout` の ID（例: 28）になり、無関係なビューを指してしまう
3. `company.external_report_layout_id.sudo().key` が空となり、`t-call` で `template is required` が発生

## 技術的な問題分析

### 1. レイアウト参照の不整合
- `res.company.external_report_layout_id` は本来 `ir.ui.view` を指すべきだが、統合コードが `report.layout` の ID を直接書き込んでいた
- 偶然一致した ID が別ビュー（例: `ir.cron` ツリー）を指し、`sudo().key` が空文字となり QWeb がテンプレートを見つけられない

### 2. 復元処理の連鎖不具合
- 過去レイアウト保持用フィールドも `report.layout` の ID を保存しており、切り替え操作のたびに誤った ID が再適用される
- 結果としてデータベースを修正しても UI 操作で直ちに再発する状態だった

### 3. 二次的影響
- Document Layout ウィザード、請求書プレビュー、メール送信テンプレートなど `external_report_layout_id` を参照する全箇所で同じ例外が発生
- 問題が拡散し、Japan レイアウト以外を選択した場合でも同一エラーが継続

## 解決策の検討

### 即座に試すべき解決策

1. **モジュール更新**
   - `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u l10n_jp_invoice_system --stop-after-init`
   - 新コードがビュー ID 書き込みと自動修復を提供
2. **既存データの補正**
   - `env['res.company']._acoona_invoice_fix_external_layout_pointer()` を実行し、誤った ID を対応するビュー ID に置換
   - 必要に応じて SQL で `external_report_layout_id` を `report.layout.view_id` と同期
3. **動作確認**
   - 会社設定 → 帳票レイアウトで期待するビューを指しているか確認
   - Document Layout ウィザードや請求書 PDF プレビューを再検証

### 長期的な解決策

1. **ビュー ID 変換ヘルパーの導入**
   - `res_company.py` に `report.layout` ↔ `ir.ui.view` 変換ロジックを追加し常時利用
   - `base_document_layout.py` でも会社側ビューをレイアウトに解決して使用
2. **初期化と更新処理の一貫化**
   - `post_init_hook` や `_register_hook` で既存企業の参照を自動修復
   - 会社作成・設定変更のたびにビュー ID のみを保存
3. **回帰テストの整備**
   - 外部レイアウト参照が常にビュー ID かを確認するユニットテストを追加

## 次のアクション

### 優先度 1: 緊急対応
1. `l10n_jp_invoice_system` モジュールを更新して新コードを反映
2. `_acoona_invoice_fix_external_layout_pointer()` を実行し既存データを一括修復
3. 請求書プレビュー／メール送信でエラーが消えていることを現場で確認

### 優先度 2: 根本解決
1. 旧 `acoona_invoice` モジュール等に同種の書き込みが残っていないか確認
2. 追加テスト（ウィザード・請求書レポート）を自動化
3. 運用ドキュメントをビュー ID ベースに更新

### 優先度 3: 品質向上
1. 統合テストの実施
2. ドキュメントの整備
3. エラーログの監視体制構築

## 参考情報

### 関連ファイル
- `/addons/l10n_jp_invoice_system/models/res_company.py`
- `/addons/l10n_jp_invoice_system/models/base_document_layout.py`
- `/addons/l10n_jp_invoice_system/views/report_invoice_document_acoona.xml`
- `/addons/l10n_jp_invoice_system/hooks.py`

### エラーログの場所
- Odoo サーバーログ: `docker compose logs odoo`
- QWeb エラー: ブラウザの開発者ツール
- データベース状態: PostgreSQL 直接確認

## まとめ

統合作業は完了しているが、`external_report_layout_id` がビューではなく `report.layout` の ID を保持していたため、どのレイアウトを選択しても QWeb がテンプレートを解決できず例外が発生していた。モジュール更新と自動修復ヘルパーにより、常に `ir.ui.view` を参照するよう修正済み。

---

**作成日**: 2025-10-13  
**更新日**: 2025-10-12  
**ステータス**: 進行中（エラー解決中）
