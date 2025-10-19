"""
トップレベルメニューの web_icon_data を初期化するワンショットスクリプト。

使い方:
  docker compose exec odoo python /mnt/extra-addons/reset_menu_icons.py [DB名] [--all]

引数:
  DB名  : 省略時は環境変数 ODOO_DB または 'odoo'
  --all : トップレベルだけでなく、全メニューの web_icon_data を初期化

注意:
  - Odoo コンテナ内で実行されることを想定（/mnt/extra-addons にマウント）
  - 実行後はアセット再構築 (-u web) とサーバ再起動を推奨
"""

import argparse
import logging
import os 
import sys

import odoo
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

DEFAULT_DB = os.environ.get('ODOO_DB', 'odoo')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('db', nargs='?', default=DEFAULT_DB)
    parser.add_argument('--all', dest='all_menus', action='store_true', help='全メニュー対象')
    return parser.parse_args()


def main():
    args = parse_args()
    db_name = args.db

    # Odoo 設定（docker-compose.yml の構成に合わせる）
    odoo.tools.config.parse_config([
        f'--database={db_name}',
        '--db_user=odoo',
        '--db_password=odoo',
        '--db_host=db',
        '--addons-path=/mnt/extra-addons',
    ])

    try:
        registry = Registry.new(db_name, update_module=False)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            domain = [] if args.all_menus else [('parent_id', '=', False)]
            menus = env['ir.ui.menu'].search(domain)
            if not menus:
                logger.info('対象メニューが見つかりませんでした（domain=%s）', domain)
                return
            logger.info('メニュー件数: %d / web_icon_data を初期化します', len(menus))
            menus.write({'web_icon_data': False})
            cr.commit()
            logger.info('完了: web_icon_data を初期化しました')
    except Exception as exc:
        logger.error('エラー: %s', exc)
        sys.exit(1)


if __name__ == '__main__':
    main()

