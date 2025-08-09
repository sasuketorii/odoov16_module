# 日本都道府県ローカライズモジュール

## 概要
このモジュールは、Odoo16の連絡先（res.partner）で日本を選択した際に表示される都道府県名を、英語表記から日本語表記に自動変換します。

## 主な機能
- 47都道府県すべての日本語名称を設定
- 都道府県コードを全国地方公共団体コード（01〜47）に統一
- インストール時に既存データを自動更新

## 変換例
| 変換前（英語） | 変換後（日本語） | コード |
|---------------|----------------|--------|
| Hokkaido | 北海道 | 01 |
| Aomori | 青森県 | 02 |
| Iwate | 岩手県 | 03 |
| Miyagi | 宮城県 | 04 |
| Akita | 秋田県 | 05 |
| ... | ... | ... |
| Okinawa | 沖縄県 | 47 |

## インストール方法

### 1. モジュールの配置
```bash
# addonsディレクトリに配置
cp -r jp_prefecture_localization /path/to/odoo/addons/
```

### 2. Odooの再起動
```bash
# Dockerを使用している場合
docker-compose restart odoo
```

### 3. アプリリストの更新
1. Odooにログイン
2. 「Apps」メニューへ移動
3. 「Update Apps List」をクリック

### 4. モジュールのインストール
1. 検索バーで「日本都道府県」または「prefecture」を検索
2. 「日本都道府県ローカライズ」モジュールを見つける
3. 「Install」ボタンをクリック

## 使用方法
インストール後は自動的に適用されます：
1. 連絡先（Contacts）を開く
2. 新規作成または既存の連絡先を編集
3. 国で「日本」を選択
4. 都道府県ドロップダウンに日本語名が表示されます

## 技術仕様

### データ構造
- **モデル**: `res.country.state`
- **対象国**: 日本（base.jp）
- **更新方法**: XMLデータファイルとpost_init_hook

### ファイル構成
```
jp_prefecture_localization/
├── __init__.py
├── __manifest__.py
├── hooks.py
├── data/
│   └── res_country_state_data.xml
├── security/
│   └── ir.model.access.csv
├── i18n/
│   └── ja.po
└── README.md
```

## 注意事項
- このモジュールは既存の都道府県データを上書きします
- アンインストール後も日本語名は保持されます
- 他のモジュールとの干渉はありません

## ライセンス
LGPL-3

## 作成者
- **Author**: SasukeTorii
- **Company**: REV-C inc.
- **Website**: https://company.rev-c.com

## サポート
問題や質問がある場合は、GitHubのIssueセクションでお知らせください。