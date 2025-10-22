# -*- coding: utf-8 -*-
"""アプリ一覧から Enterprise 専用モジュールを除外する。"""

from odoo import api, models


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        domain = list(domain or []) + [("to_buy", "=", False)]
        return super().search(domain, offset=offset, limit=limit, order=order, count=count)
