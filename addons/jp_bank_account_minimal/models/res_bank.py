# -*- coding: utf-8 -*-
from odoo import models, fields

class ResBank(models.Model):
  _inherit = 'res.bank'

  isJapanese = fields.Boolean('日本の銀行', default=True, help='日本用マスタであることを示す') 