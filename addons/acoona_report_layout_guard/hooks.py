# -*- coding: utf-8 -*-
"""
インストール時とアンインストール時に、会社の帳票レイアウト参照を整合させるフック。
"""

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """モジュール導入時に既存会社のレイアウト参照を補正。"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.company"].sudo()._rlg_guard_external_layout_pointer()


def uninstall_hook(cr, registry):
    """アンインストール時は標準レイアウトへ戻し、不整合を残さない。"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.company"].sudo()._rlg_reset_to_standard_layout()
