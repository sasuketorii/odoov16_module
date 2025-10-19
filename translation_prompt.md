# Odoo v16 日本語翻訳修正プロンプト

## タスク概要
Odoo v16の日本語翻訳ファイル（`odoo16_base_ja.po`）内の不自然な翻訳を修正してください。

## ファイル情報
- **ファイル**: `odoo16_base_ja.po`
- **総行数**: 37,432行
- **日本語翻訳行数**: 約929行
- **対象**: `msgstr "日本語翻訳"` の形式

## 修正が必要な問題パターン

### 1. 長音記号抜け
- 「ユーザ」→「ユーザー」
- 「サーバ」→「サーバー」
- 「フィルタ」→「フィルター」
- 「プロバイダ」→「プロバイダー」
- 「プリンタ」→「プリンター」
- 「パートナ」→「パートナー」
- 「コンピュータ」→「コンピューター」
- 「オーダ」→「オーダー」

### 2. 日本の商習慣に合わない用語
- 「購買」→「仕入/発注」
- 「購買管理」→「仕入管理」
- 「購買契約」→「仕入契約」
- 「プロジェクト購買」→「プロジェクト仕入」
- 「フリート」→「車両管理」
- 「艦隊の歴史」→「車両履歴」

### 3. 不自然な表現
- 「受け入れられたユーザー」→「承認されたユーザー」
- 「プロファイル」→「プロフィール」
- 「Googleカレンダ」→「Googleカレンダー」
- 「フラグ画像のURL」→「国旗画像URL」

### 4. 冗長な表現
- 「〜することができます」→「〜できます」
- 「〜することができます」→「〜できます」

### 5. 不自然な人称表現
- 「あなたのウェブサイト」→「ウェブサイト」
- 「あなたの顧客」→「顧客」

## 修正方法

### 手順1: 日本語翻訳行の抽出
```bash
grep -n 'msgstr.*[ひらがなカタカナ漢字]' odoo16_base_ja.po > japanese_translations.txt
```

### 手順2: 問題のある翻訳の特定
抽出した翻訳を上記のパターンに照らし合わせて確認

### 手順3: 一括置換
```bash
# 長音記号抜けの修正例
sed -i 's/msgstr "ユーザ"/msgstr "ユーザー"/g' odoo16_base_ja.po
sed -i 's/msgstr "サーバ"/msgstr "サーバー"/g' odoo16_base_ja.po
sed -i 's/msgstr "フィルタ"/msgstr "フィルター"/g' odoo16_base_ja.po
sed -i 's/msgstr "プロバイダ"/msgstr "プロバイダー"/g' odoo16_base_ja.po
sed -i 's/msgstr "プリンタ"/msgstr "プリンター"/g' odoo16_base_ja.po
sed -i 's/msgstr "パートナ"/msgstr "パートナー"/g' odoo16_base_ja.po
sed -i 's/msgstr "コンピュータ"/msgstr "コンピューター"/g' odoo16_base_ja.po
sed -i 's/msgstr "オーダ"/msgstr "オーダー"/g' odoo16_base_ja.po

# 日本の商習慣に合わない用語の修正
sed -i 's/msgstr "購買"/msgstr "仕入"/g' odoo16_base_ja.po
sed -i 's/msgstr "購買管理"/msgstr "仕入管理"/g' odoo16_base_ja.po
sed -i 's/msgstr "購買契約"/msgstr "仕入契約"/g' odoo16_base_ja.po
sed -i 's/msgstr "プロジェクト購買"/msgstr "プロジェクト仕入"/g' odoo16_base_ja.po
sed -i 's/msgstr "フリート"/msgstr "車両管理"/g' odoo16_base_ja.po
sed -i 's/msgstr "艦隊の歴史"/msgstr "車両履歴"/g' odoo16_base_ja.po

# 不自然な表現の修正
sed -i 's/msgstr "受け入れられたユーザー"/msgstr "承認されたユーザー"/g' odoo16_base_ja.po
sed -i 's/msgstr "プロファイル"/msgstr "プロフィール"/g' odoo16_base_ja.po
sed -i 's/msgstr "Googleカレンダ"/msgstr "Googleカレンダー"/g' odoo16_base_ja.po
sed -i 's/msgstr "フラグ画像のURL"/msgstr "国旗画像URL"/g' odoo16_base_ja.po

# 冗長な表現の修正
sed -i 's/msgstr "\([^"]*\)することができます"/msgstr "\1できます"/g' odoo16_base_ja.po

# 不自然な人称表現の修正
sed -i 's/msgstr "あなたのウェブサイト"/msgstr "ウェブサイト"/g' odoo16_base_ja.po
sed -i 's/msgstr "あなたの顧客"/msgstr "顧客"/g' odoo16_base_ja.po
```

### 手順4: 個別修正
一括置換で対応できない特殊なケースを個別に修正

## 注意事項

1. **バックアップ**: 修正前に必ずファイルのバックアップを作成
2. **段階的実行**: 一度に全て修正せず、パターンごとに段階的に実行
3. **確認**: 各修正後に結果を確認
4. **テスト**: 修正後の整合性を確認

## 期待される結果

- 日本人ユーザーにとって自然で理解しやすい翻訳
- 日本の商習慣に合ったビジネス用語の統一
- 機械翻訳の不自然さを解消
- 一貫した翻訳ルールの確立

## 完了後の確認

1. 修正された翻訳の品質確認
2. 構文エラーの有無確認
3. 翻訳の整合性確認
4. テスト実行

## 連絡先
修正完了後は、修正内容のサマリーとともに報告してください。
