# Odoo16 開発ガイドライン

## 🎯 開発目的
- **Odoo v16**専用のモジュール開発
- **他モジュールへの干渉を最小限**にする設計
- **日本ローカライズ**に特化した機能実装

---

## 📁 プロジェクト構成

```
/Users/sasuketorii/Odoo16-0805/
├── docker-compose.yml
├── config/
│   └── odoo.conf
├── addons/                      # カスタムモジュール配置場所
│   ├── sasuke_backend_theme/    # カスタムテーマ（作成済み）
│   └── [新規モジュール]/
└── CLAUDE.md                     # このファイル
```

## 🐳 Docker環境

### コンテナ情報
- **Odoo**: odoo16-0805-odoo-1 (Port: 8069)
- **PostgreSQL**: odoo16-0805-db-1 (Port: 5432)

### 基本コマンド
```bash
# コンテナ起動
docker-compose up -d

# コンテナ再起動
docker-compose restart odoo

# ログ確認
docker-compose logs -f odoo

# モジュール更新
docker exec odoo16-0805-odoo-1 odoo -c /etc/odoo/odoo.conf -u [module_name] --stop-after-init
```

---

## 🛠️ Odoo16 モジュール開発規則

### 1. モジュール構造（必須）

```
module_name/
├── __init__.py
├── __manifest__.py
├── security/
│   └── ir.model.access.csv      # アクセス権限
├── models/
│   ├── __init__.py
│   └── model_name.py
├── views/
│   ├── menu_views.xml           # メニュー定義
│   └── model_views.xml          # ビュー定義
├── data/
│   └── data.xml                 # 初期データ
├── i18n/
│   └── ja.po                    # 日本語翻訳
└── static/
    └── description/
        └── icon.png              # モジュールアイコン
```

### 2. __manifest__.py テンプレート

```python
# -*- coding: utf-8 -*-
{
    'name': 'モジュール名（日本語）',
    'version': '16.0.1.0.0',
    'category': 'Localization/Japan',
    'summary': '簡潔な説明',
    'description': """
詳細な説明（日本語）
====================
- 機能1
- 機能2
    """,
    'author': 'SasukeTorii',
    'company': 'REV-C inc.',
    'maintainer': 'REV-C inc.',
    'website': 'https://company.rev-c.com',
    'depends': ['base'],  # 最小限の依存関係
    'data': [
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/model_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
```

### 3. モデル開発原則

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ModelName(models.Model):
    _name = 'module.model'
    _description = 'モデルの説明（日本語）'
    _order = 'id desc'
    _rec_name = 'name'
    
    # 必須フィールド
    name = fields.Char('名称', required=True)
    active = fields.Boolean('有効', default=True)
    
    # 日本特有のフィールド例
    name_kana = fields.Char('名称（カナ）')
    postal_code = fields.Char('郵便番号', size=8)
    
    @api.constrains('postal_code')
    def _check_postal_code(self):
        """郵便番号の形式チェック"""
        for record in self:
            if record.postal_code and not record._validate_postal_code(record.postal_code):
                raise ValidationError(_('郵便番号の形式が正しくありません。'))
```

---

## 🇯🇵 日本ローカライズ要件

### 1. 必須対応項目
- **文字コード**: UTF-8（必須）
- **日付形式**: YYYY/MM/DD または YYYY年MM月DD日
- **通貨**: 円（JPY）、小数点なし
- **住所形式**: 郵便番号 → 都道府県 → 市区町村 → 番地
- **名前形式**: 姓 → 名の順序
- **ふりがな**: 重要な名称にはカナフィールドを追加

### 2. UI/UX設計
- **ラベル**: 日本語で簡潔に
- **ヘルプテキスト**: 必要に応じて日本語で補足
- **エラーメッセージ**: 日本語で明確に
- **確認ダイアログ**: 「はい」「いいえ」を使用

### 3. ビジネスロジック
- **消費税**: 10%（軽減税率8%対応も考慮）
- **会計年度**: 4月〜3月
- **印鑑文化**: 承認フローで考慮
- **敬語**: システムメッセージは丁寧語を使用

---

## 🔒 他モジュール非干渉の原則

### 1. 継承時の注意
```python
# ❌ 悪い例：既存フィールドを直接変更
class ResPartner(models.Model):
    _inherit = 'res.partner'
    name = fields.Char(required=False)  # 既存を変更

# ✅ 良い例：新しいフィールドを追加
class ResPartner(models.Model):
    _inherit = 'res.partner'
    name_kana = fields.Char('名前（カナ）')  # 追加のみ
```

### 2. ビュー継承のルール
```xml
<!-- ✅ 良い例：position属性で追加 -->
<record id="view_partner_form_inherit" model="ir.ui.view">
    <field name="name">res.partner.form.inherit.japan</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <field name="name" position="after">
            <field name="name_kana"/>
        </field>
    </field>
</record>
```

### 3. 依存関係の最小化
- `depends`は必要最小限に
- 標準モジュールの上書きは避ける
- 独自の名前空間を使用（例：`jp_*`、`sasuke_*`）

---

## 💬 コミュニケーションプロトコル

### Discussion-First Protocol
- コメントや疑問を共有したら、まず対話から始めてください
- すぐにコード修正を始めないでください  
- 私の意図を確認し、複数の選択肢を提示してください
- 実装前に「これから○○を実装します」と宣言し、承認を待ってください
- 「実装して」「修正して」「やって」などの明確な指示があるまでコードを書かないでください
- 私のコメントは思考の整理や相談かもしれません。全てが実装指示ではありません

### 🔍 問題解決アプローチ

#### 根本解決の原則
- **対症療法を避ける**: エラーが出た箇所だけを修正するのではなく、なぜそのエラーが発生したのか根本原因を特定する
- **影響範囲の確認**: 修正が他の機能に与える影響を必ず確認する
- **整合性の維持**: 一部分の修正が全体の設計思想や既存の実装と矛盾しないか検証する

#### 問題分析の手順
1. **現象の把握**: 何が起きているか
2. **原因の特定**: なぜ起きているか（5回のなぜを問う）
3. **影響範囲**: この問題/修正が影響する範囲はどこまでか
4. **解決策の検討**: 
   - Quick Fix（応急処置）
   - Proper Solution（適切な解決）
   - Best Practice（最善の方法）
5. **実装方針の決定**: 上記を説明した上で、どのアプローチを取るか相談

#### 例
```
❌ 悪い例：
「エラーが出たので、try-catchで囲みました」

✅ 良い例：
「このエラーは○○が原因で発生しています。
解決方法として：
1. 応急処置：エラーハンドリングを追加
2. 適切な解決：データ検証を入力時点で実施
3. 最善策：入力フォームの設計を見直し
どのアプローチを取りますか？」
```

### 実装指示キーワード
明確に実装を求める場合：
- 実装して / 修正して / 変更して / 作成して
- やって / お願い / 頼む
- Go ahead / Please implement

### 相談・検討キーワード  
対話や意見を求める場合：
- どう思う？ / どうかな？ / ～じゃない？
- 意見を聞きたい / 相談したい
- もしかして / たぶん / かもしれない

---

## 📝 開発チェックリスト

### 新規モジュール作成時
- [ ] モジュール名は他と競合しない独自名
- [ ] __manifest__.pyに適切な情報記載
- [ ] security/ir.model.access.csvでアクセス権限設定
- [ ] i18n/ja.poで日本語翻訳
- [ ] README.rstまたはREADME.mdでドキュメント作成

### 🎯 品質保証チェックリスト

修正・実装前に確認：
- [ ] 根本原因を特定したか
- [ ] 他の機能への影響を検討したか
- [ ] 既存の設計思想と一致しているか
- [ ] より良い解決方法がないか検討したか
- [ ] 将来的な拡張性を考慮したか

### コード品質
- [ ] PEP 8準拠
- [ ] 適切なコメント（日本語OK）
- [ ] エラーハンドリング実装
- [ ] ログ出力の適切な使用

### テスト
- [ ] 単体での動作確認
- [ ] 他モジュールへの影響確認
- [ ] アンインストール可能か確認
- [ ] データの整合性確認

---

## 🚀 よく使うコマンド

```bash
# 新規モジュール作成
mkdir -p addons/module_name/{models,views,security,data,i18n,static/description}

# 権限ファイル生成
echo "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink" > addons/module_name/security/ir.model.access.csv

# モジュール一覧更新
docker exec odoo16-0805-odoo-1 odoo -c /etc/odoo/odoo.conf --update-list

# 特定モジュールインストール
docker exec odoo16-0805-odoo-1 odoo -c /etc/odoo/odoo.conf -i module_name --stop-after-init

# ログ監視
docker-compose logs -f odoo | grep -i error
```

---

## 📚 参考リソース

- [Odoo 16 Documentation](https://www.odoo.com/documentation/16.0/)
- [Odoo 16 API Reference](https://www.odoo.com/documentation/16.0/developer.html)
- [日本Odooユーザー会](https://odoo.jp/)

---

## 🔧 トラブルシューティング

### モジュールが認識されない
1. `__init__.py`が存在するか確認
2. `__manifest__.py`の記述を確認
3. Dockerコンテナを再起動
4. Apps Listを更新

### インストールエラー
1. `depends`の依存関係を確認
2. XMLファイルの構文エラーをチェック
3. Pythonファイルのインポートエラーを確認
4. ログを確認：`docker-compose logs odoo`

### 日本語が文字化けする
1. ファイルのエンコーディングがUTF-8か確認
2. `# -*- coding: utf-8 -*-`がファイル先頭にあるか確認
3. i18n/ja.poファイルの設定を確認

---

## 📅 更新履歴

- 2024-08-07: 初版作成
- sasuke_backend_theme作成完了
- 縦横センタリング問題修正済み

---

## 🎯 次のステップ

1. **基本モジュールの作成**
   - 日本の住所管理モジュール
   - 日本の祝日カレンダーモジュール
   - 和暦対応モジュール

2. **ビジネスモジュール**
   - 請求書の日本フォーマット対応
   - 見積書テンプレート
   - 納品書・受領書管理

3. **連携モジュール**
   - 会計ソフト連携
   - 銀行API連携
   - 電子帳簿保存法対応

---

## 💡 開発のコツ

1. **小さく始める**: 最初は単純な機能から実装
2. **標準を活用**: Odooの標準機能を最大限活用
3. **ドキュメント重視**: コードと同じくらいドキュメントも重要
4. **コミュニティ活用**: 日本のOdooコミュニティと情報交換
5. **テスト駆動**: テストケースを先に考える

---

**Author**: SasukeTorii | REV-C inc.
**Last Updated**: 2024-08-07