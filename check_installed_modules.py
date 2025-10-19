#!/usr/bin/env python3
"""
インストール済みのブランディング関連モジュールを確認するスクリプト
"""

import sys
import odoorpc

# Odoo接続設定
ODOO_HOST = 'localhost'
ODOO_PORT = 8069
ODOO_DATABASE = 'odoo'
ODOO_USER = 'admin'
ODOO_PASSWORD = 'admin'

def checkInstalledModules():
  """インストール済みモジュールを確認する"""
  try:
    # Odooに接続
    odoo = odoorpc.ODOO(ODOO_HOST, port=ODOO_PORT)
    odoo.login(ODOO_DATABASE, ODOO_USER, ODOO_PASSWORD)

    # モジュールモデルを取得
    moduleModel = odoo.env['ir.module.module']

    # ブランディング関連モジュールを検索
    keywords = ['brand', 'debrand', 'theme', 'acoona', 'sasuke']
    allModules = []

    for keyword in keywords:
      moduleIds = moduleModel.search([
        ('state', '=', 'installed'),
        ('name', 'ilike', keyword)
      ])
      modules = moduleModel.browse(moduleIds)
      for module in modules:
        if module.id not in [m['id'] for m in allModules]:
          allModules.append({
            'id': module.id,
            'name': module.name,
            'state': module.state,
            'shortdesc': module.shortdesc
          })

    # 結果を表示
    print("インストール済みブランディング関連モジュール:")
    print("-" * 70)
    for module in sorted(allModules, key=lambda x: x['name']):
      print(f"{module['name']:40s} | {module['state']:12s}")
      print(f"  -> {module['shortdesc']}")
      print()

    return True

  except Exception as e:
    print(f"エラー: {e}", file=sys.stderr)
    print("OdooRPCがインストールされていない可能性があります。")
    print("pip install odoorpc でインストールしてください。")
    return False

if __name__ == '__main__':
  checkInstalledModules()

