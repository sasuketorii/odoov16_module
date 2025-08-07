# Odoo16 Japanese Localization Modules

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Odoo 16](https://img.shields.io/badge/odoo-16.0-purple.svg)](https://www.odoo.com/)

日本向けのOdoo16カスタムモジュール集です。日本のビジネス慣習と法規制に対応したモジュールを提供します。

## 🎯 プロジェクト目標

- **Odoo v16専用**のモジュール開発
- **他モジュールへの干渉を最小限**にする設計
- **日本ローカライズ**に特化した機能実装

## 📦 含まれるモジュール

### ✅ 完成済み
- **sasuke_backend_theme**: 改良されたバックエンドテーマ
  - 縦横センタリング問題修正
  - デザイン整合性向上
  - レスポンシブ対応

### 🚧 開発予定
- **日本住所管理モジュール**: 郵便番号・都道府県・市区町村の管理
- **日本祝日カレンダー**: 祝日・休日の自動反映
- **和暦対応モジュール**: 令和・平成等の元号対応
- **請求書日本フォーマット**: 日本の商習慣に対応した書式
- **消費税計算モジュール**: 軽減税率対応

## 🛠️ 環境要件

- Docker & Docker Compose
- Odoo 16.0
- PostgreSQL 13
- Python 3.8+

## 🚀 セットアップ

### 1. リポジトリクローン
```bash
git clone https://github.com/sasuketorii/odoov16_module.git
cd odoov16_module
```

### 2. Docker環境起動
```bash
docker-compose up -d
```

### 3. Odooアクセス
- URL: http://localhost:8069
- ユーザー: admin
- パスワード: admin

## 📁 プロジェクト構造

```
.
├── docker-compose.yml       # Docker構成
├── config/
│   └── odoo.conf            # Odoo設定
├── addons/                  # カスタムモジュール
│   └── sasuke_backend_theme/
├── CLAUDE.md                # 開発ガイドライン
└── README.md                # このファイル
```

## 🔧 開発ガイドライン

詳細な開発ガイドラインは [CLAUDE.md](./CLAUDE.md) を参照してください。

### 重要な原則
1. **他モジュール非干渉**: 既存モジュールの変更は行わない
2. **日本ローカライズ**: 日本の法規制・商習慣に準拠
3. **最小依存**: 依存関係は必要最小限に抑制

## 📝 モジュール開発手順

### 1. 新規モジュール作成
```bash
mkdir -p addons/module_name/{models,views,security,data,i18n,static/description}
```

### 2. 基本ファイル作成
- `__init__.py`
- `__manifest__.py`
- `security/ir.model.access.csv`
- `i18n/ja.po`

### 3. モジュールインストール
```bash
# コンテナ内でモジュール更新
docker exec odoo16-0805-odoo-1 odoo -c /etc/odoo/odoo.conf -u module_name --stop-after-init
```

## 🌐 日本ローカライズ対応

### 対応済み項目
- UTF-8文字コード
- 日本語UI対応
- レスポンシブデザイン

### 今後対応予定
- 日本の住所形式（郵便番号→都道府県→市区町村）
- 和暦表示
- 消費税計算（軽減税率対応）
- 日本の会計年度（4月〜3月）
- 印鑑・承認フロー

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはLGPL-3ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 👥 作成者

**SasukeTorii**
- Company: REV-C inc.
- Website: https://company.rev-c.com

## 📚 参考リンク

- [Odoo 16 Documentation](https://www.odoo.com/documentation/16.0/)
- [日本Odooユーザー会](https://odoo.jp/)
- [Odoo Developer Documentation](https://www.odoo.com/documentation/16.0/developer.html)

## 📊 バージョン履歴

### v0.0.1 (2024-08-07)
- 初版リリース
- sasuke_backend_theme完成
- 基本的な開発環境構築
- CLAUDE.md開発ガイドライン作成

---

**Note**: このプロジェクトは継続的に開発中です。日本のOdooユーザーコミュニティの発展に貢献することを目指しています。