# -*- coding: utf-8 -*-
{
  'name': '日本銀行口座（最小構成）',
  'version': '16.0.1.0.0',
  'category': 'Localization/Japan',
  'summary': '日本の実務向け、最小5項目の銀行口座登録',
  'description': '銀行・支店・口座種別・口座番号・名義カナのみで運用する最小構成',
  'author': 'SasukeTorii',
  'website': 'https://company.rev-c.com',
  'license': 'LGPL-3',
  'depends': ['base', 'contacts'],
  'data': [
    'security/ir.model.access.csv',
    'views/res_partner_bank_views.xml',
  ],
  'installable': True,
  'application': False,
} 