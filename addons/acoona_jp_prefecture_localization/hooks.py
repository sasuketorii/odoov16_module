# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

OLD_MODULE_NAME = 'jp_prefecture_localization'
NEW_MODULE_NAME = 'acoona_jp_prefecture_localization'


def pre_init_hook(cr):
    """以前のモジュール名から新モジュール名へ参照を移行"""
    module_id = None

    cr.execute(
        "SELECT id FROM ir_module_module WHERE name = %s",
        (OLD_MODULE_NAME,),
    )
    old_row = cr.fetchone()

    cr.execute(
        "SELECT id FROM ir_module_module WHERE name = %s",
        (NEW_MODULE_NAME,),
    )
    new_row = cr.fetchone()

    if old_row:
        module_id = old_row[0]
        if new_row and new_row[0] != module_id:
            cr.execute(
                "DELETE FROM ir_module_module WHERE id = %s",
                (new_row[0],),
            )
        cr.execute(
            "UPDATE ir_module_module SET name = %s WHERE id = %s",
            (NEW_MODULE_NAME, module_id),
        )
    elif new_row:
        module_id = new_row[0]

    for table, column in (
        ("ir_model_data", "module"),
        ("ir_translation", "module"),
        ("ir_module_module_dependency", "name"),
        ("ir_module_module_shortcut", "name"),
    ):
        cr.execute("SELECT to_regclass(%s)", (table,))
        if not cr.fetchone()[0]:
            continue
        cr.execute(
            f"UPDATE {table} SET {column} = %s WHERE {column} = %s",
            (NEW_MODULE_NAME, OLD_MODULE_NAME),
        )

    _logger.info(
        "Renamed module %s references to %s (module_id=%s)",
        OLD_MODULE_NAME,
        NEW_MODULE_NAME,
        module_id if module_id else 'n/a',
    )


def post_init_hook(cr, registry):
    """
    インストール後に実行されるフック
    既存の都道府県データを日本語に更新または新規作成
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # 日本の国レコードを取得
    japan = env.ref('base.jp', raise_if_not_found=False)
    if not japan:
        _logger.warning('Japan country record not found')
        return
    
    # 既存の都道府県データを英語名から日本語名にマッピング
    prefecture_mapping = {
        'Hokkaido': ('北海道', '01'),
        'Aomori': ('青森県', '02'),
        'Iwate': ('岩手県', '03'),
        'Miyagi': ('宮城県', '04'),
        'Akita': ('秋田県', '05'),
        'Yamagata': ('山形県', '06'),
        'Fukushima': ('福島県', '07'),
        'Ibaraki': ('茨城県', '08'),
        'Tochigi': ('栃木県', '09'),
        'Gunma': ('群馬県', '10'),
        'Saitama': ('埼玉県', '11'),
        'Chiba': ('千葉県', '12'),
        'Tokyo': ('東京都', '13'),
        'Kanagawa': ('神奈川県', '14'),
        'Niigata': ('新潟県', '15'),
        'Toyama': ('富山県', '16'),
        'Ishikawa': ('石川県', '17'),
        'Fukui': ('福井県', '18'),
        'Yamanashi': ('山梨県', '19'),
        'Nagano': ('長野県', '20'),
        'Gifu': ('岐阜県', '21'),
        'Shizuoka': ('静岡県', '22'),
        'Aichi': ('愛知県', '23'),
        'Mie': ('三重県', '24'),
        'Shiga': ('滋賀県', '25'),
        'Kyoto': ('京都府', '26'),
        'Osaka': ('大阪府', '27'),
        'Hyogo': ('兵庫県', '28'),
        'Nara': ('奈良県', '29'),
        'Wakayama': ('和歌山県', '30'),
        'Tottori': ('鳥取県', '31'),
        'Shimane': ('島根県', '32'),
        'Okayama': ('岡山県', '33'),
        'Hiroshima': ('広島県', '34'),
        'Yamaguchi': ('山口県', '35'),
        'Tokushima': ('徳島県', '36'),
        'Kagawa': ('香川県', '37'),
        'Ehime': ('愛媛県', '38'),
        'Kochi': ('高知県', '39'),
        'Fukuoka': ('福岡県', '40'),
        'Saga': ('佐賀県', '41'),
        'Nagasaki': ('長崎県', '42'),
        'Kumamoto': ('熊本県', '43'),
        'Oita': ('大分県', '44'),
        'Miyazaki': ('宮崎県', '45'),
        'Kagoshima': ('鹿児島県', '46'),
        'Okinawa': ('沖縄県', '47'),
    }
    
    # 既存の都道府県レコードを更新または新規作成
    for eng_name, (jp_name, jp_code) in prefecture_mapping.items():
        # コードで検索（既存レコードがある場合）
        state = env['res.country.state'].search([
            ('country_id', '=', japan.id),
            ('code', '=', jp_code)
        ], limit=1)
        
        if not state:
            # 英語名で検索
            state = env['res.country.state'].search([
                ('country_id', '=', japan.id),
                ('name', '=', eng_name)
            ], limit=1)
        
        if state:
            # 既存レコードを更新
            state.write({
                'name': jp_name,
                'code': jp_code
            })
            _logger.info(f'Updated {eng_name} to {jp_name} [{jp_code}]')
        else:
            # 新規作成
            env['res.country.state'].create({
                'name': jp_name,
                'code': jp_code,
                'country_id': japan.id
            })
            _logger.info(f'Created {jp_name} [{jp_code}]')
    
    cr.commit()
    
    _logger.info('Japanese prefecture localization completed successfully')
