from odoo import api, fields, models


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    acoona_material_icon = fields.Char(
        string="Material Icon",
        help="Material Symbols icon name used by the Acoona sidebar.",
    )

    def _load_menus_prepare_values(self, menu):
        values = super()._load_menus_prepare_values(menu)
        values["acoona_material_icon"] = menu.acoona_material_icon or False
        return values

    @api.model
    def _acoona_apply_default_icons(self):
        """Set default Material icon names on known application menus."""
        icon_map = {
            "base.menu_apps": "apps",
            "base.menu_board_root": "dashboard",
            "base.menu_settings": "settings",
            "mail.menu_root_discuss": "chat",
            "contacts.menu_contacts": "contact_page",
            "crm.crm_menu_root": "diversity_3",
            "sale.sale_menu_root": "shopping_cart",
            "purchase.menu_purchase_root": "shopping_bag",
            "account.menu_finance": "account_balance",
            "stock.menu_stock_root": "inventory_2",
            "mrp.menu_mrp_root": "precision_manufacturing",
            "project.menu_main_pm": "assignment",
            "hr.menu_hr_root": "badge",
            "hr_timesheet.menu_hr_timesheet_root": "schedule",
            "hr_expense.menu_hr_expense_root": "receipt_long",
            "hr_holidays.menu_hr_holidays_root": "beach_access",
            "hr_attendance.menu_hr_attendance_root": "how_to_reg",
            "hr_recruitment.menu_hr_recruitment_root": "work",
            "hr_payroll.menu_hr_payroll_root": "payments",
            "approvals.menu_approvals_root": "task_alt",
            "helpdesk.helpdesk_menu_root": "support_agent",
            "maintenance.menu_maintenance_root": "build_circle",
            "quality_control.menu_quality_root": "fact_check",
            "mrp_repair.menu_mrp_repair_root": "handyman",
            "point_of_sale.menu_point_root": "sell",
            "website.menu_website": "public",
            "website_sale.menu_website_sale": "storefront",
            "website_slides.menu_website_slides_root": "school",
            "event.menu_event_root": "event",
            "marketing_automation.menu_marketing_automation_root": "insights",
            "mass_mailing.mass_mailing_root": "mail",
            "sms.menu_sms_root": "sms",
            "social.menu_social_main": "share",
            "livechat.mail_livechat_channel_menu": "forum",
            "calendar.mail_menu_calendar": "calendar_month",
            "notes.menu_notes": "sticky_note_2",
            "sign.sign_menu_root": "edit_square",
            "sale_renting.rental_menu_root": "car_rental",
            "fsm.menu_fsm_root": "handyman",
            "planning.menu_planning_root": "calendar_view_week",
            "account_budget.menu_finance_budget_root": "account_balance_wallet",
            "account_asset.menu_finance_assets": "account_balance_wallet",
            "account_accountant.board_redirect": "query_stats",
            "l10n_jp_invoice_system.menu_root": "description",
            "acoona_invoice.menu_root": "receipt_long",
            "acoona_theme.menu_settings": "brush",
        }
        for xmlid, icon in icon_map.items():
            menu = self.env.ref(xmlid, raise_if_not_found=False)
            if menu and not menu.acoona_material_icon:
                menu.acoona_material_icon = icon
