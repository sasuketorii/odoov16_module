import os

import odoo
from odoo import SUPERUSER_ID, api
from odoo.modules.module import get_module_path
from odoo.service import db as service_db
from odoo.tools import config
from odoo.tools.translate import trans_load

# 対象言語: 日本語 (日本) を優先し、必要に応じてプレーンな ja もサポート
MODULE_NAME = "acoona_l10n_base_translations"
TARGET_LANG_CODES = ("ja_JP", "ja")
CSV_RELATIVE_PATH = os.path.join("i18n", "ja_JP.csv")


def _load_translations(cr):
    """指定された CSV 翻訳ファイルを上書きモードで読み込み反映する。"""
    module_path = get_module_path(MODULE_NAME)
    if not module_path:
        return
    csv_path = os.path.join(module_path, CSV_RELATIVE_PATH)
    if not os.path.exists(csv_path):
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    available_langs = set(
        env["res.lang"]
        .sudo()
        .search([("code", "in", list(TARGET_LANG_CODES))])
        .mapped("code")
    )
    if not available_langs:
        return

    for lang_code in available_langs:
        trans_load(cr, csv_path, lang_code, verbose=False, overwrite=True)


def _module_is_present(cr):
    cr.execute(
        """
            SELECT 1
              FROM ir_module_module
             WHERE name = %s
               AND state IN ('installed', 'to upgrade', 'to install')
             LIMIT 1
        """,
        (MODULE_NAME,),
    )
    return bool(cr.fetchone())


def _load_translations_for_db(db_name):
    with api.Environment.manage():
        registry = odoo.registry(db_name)
        with registry.cursor() as cr:
            if _module_is_present(cr):
                _load_translations(cr)


def _iter_target_databases():
    db_name = config.get("db_name")
    if db_name:
        return [db_name]
    return service_db.list_dbs()


def post_init_hook(cr, registry):
    _load_translations(cr)


def post_load():
    # 翻訳処理を一時的に無効化（読み込み速度改善のため）
    # for db_name in _iter_target_databases():
    #     _load_translations_for_db(db_name)
    pass
