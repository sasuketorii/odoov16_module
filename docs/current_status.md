# acoona_theme / acoona_branding 開発状況メモ

## 目的・やりたいこと
- 開発者モードではサイドバー（およびトップバー）に「アプリ」が表示されること。
- 開発者モードではない通常ユーザーモードでは「アプリ」だけを隠し、それ以外のアプリは表示させること。
- 上記切り替えは `acoona_branding` の Hide Developer Tools 設定値（`acoona_branding.hide_devtools`）を基準に動作させる。
- テーマ (`acoona_theme`) を有効化しても挙動が崩れないようにする。

## 現在の症状
- ブラウザは真っ白のまま。トップバー/サイドバーが描画されず、画面表示が崩壊している。
- ブラウザコンソールに次のエラーが出力されている。
	- `OwlError: Failed to compile template "web.NavBar": Unexpected identifier 'ctx'`
	- 生成されたコード中で `ctx['shouldHideAppsMenu']ctx['shouldHideAppsMenu']()` のように演算子が欠落している。
- サーバーログには対応するスタックトレースは出ていない（テンプレートのクライアントサイド変換時に失敗している）。

## 原因の切り分け結果
- 発生箇所は `addons/acoona_theme/static/src/xml/top_bar.xml` のナビバー拡張テンプレート。
- `t-if="shouldHideAppsMenu && shouldHideAppsMenu()"` と素の `&&` を記述している。
- XML 属性では `&` を `&amp;` にエスケープする必要があるため、Owl がテンプレートを JS に展開する際に論理演算子が欠落。
- その結果、展開後コード中に無効な記述が生成されて `Unexpected identifier 'ctx'` が発生している。
- サーバー側のロジック（`acoona_branding/static/src/js/menu_hide_apps.js`）は、`session.debug` と Hide Developer Tools 設定を元にメニューを除外するところまで動作しているが、フロントが壊れているため確認不能。

## 再現手順
1. `acoona_theme` モジュールをインストール／有効化した状態で Odoo を起動。
2. ブラウザからバックエンド (/web) にアクセス。
3. 画面が真っ白になりコンソールに上記 OwlError が出力される。

## 進捗とログ
- サーバー再起動ログ（2025-10-23 23:34JST）を見る限り、Odoo 自体は正常に起動できている。
- ブラウザコンソールには `[Acoona Branding] menu patch session.debug=<値> shouldHideApps=<値>` のログが出力され、サーバー側のパッチは呼ばれていることを確認。
- ただしフロント側のテンプレートエラーで描画が停止し、サイドバーが表示されない。

## 引き継ぎタスク
1. `addons/acoona_theme/static/src/xml/top_bar.xml` の `t-if` 条件を修正する。
	- 例: `t-if="shouldHideAppsMenu&amp;&amp; shouldHideAppsMenu()"` にエスケープするか、`t-if="shouldHideAppsMenu and shouldHideAppsMenu()"` のように Owl が解釈できる書き方に置き換える。
	- もしくは `t-set` で boolean 値を用意し `t-if="hide_apps"` とするなど、演算子を XML 属性に直接書かない方法を検討。
2. テンプレート修正後に `docker compose exec odoo odoo -c /etc/odoo/odoo.conf -u acoona_theme --stop-after-init --dev=all` でアセットを再生成し、コンテナを再起動して挙動を確認。
3. 開発者モード ON/OFF、それぞれでサイドバーに表示されるアプリリストを確認し、
	- 通常モード: 「アプリ」が消えて他のアプリが残ること。
	- 開発者モード: 「アプリ」を含む全アプリが表示されること。
4. `acoona_branding/static/src/js/menu_hide_apps.js` のログ出力を活用し、`session.debug` と `shouldHideApps` の値が期待通りになっているか再確認。
5. `addons/acoona_l10n_base_translations` で進めている翻訳関連の作業とも整合を取り、テーマ／ブランディング側の調整が翻訳モジュールの内容と競合しないか確認する。
6. 問題が解決したら、今回追加した `console.log` の削除や不要なデバッグコードの整理を忘れずに行う。

## 補足メモ
- すでに `acoona_branding` 側では `base.menu_apps` と `base.menu_management` を除外するようにしている。テーマ側のテンプレートも同じ配列（`apps`）を利用するよう修正済み。
- Hide Developer Tools のトグル値（`ir.config_parameter`）は DB に保存済みで、再起動しても維持される。
- これまでの作業では DB を削除していないため、既存データは保持されている。
