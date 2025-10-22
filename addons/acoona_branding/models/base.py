# -*- coding: utf-8 -*-
"""汎用モデル拡張: Enterprise 導線を含む領域の除外。"""

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        """payment.provider の有料アドオン候補を検索結果から除外する。"""
        result = super().search(domain, offset=offset, limit=limit, order=order, count=count)
        if not count and self._name == "payment.provider":
            result = result.filtered(lambda provider: not provider.module_to_buy)
        return result
