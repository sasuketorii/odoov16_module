# -*- coding: utf-8 -*-
"""Menu adjustments for developer-only entries."""

import copy

from odoo import api, models, tools


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def _is_debug_mode(self, debug_value):
        if debug_value is None:
            return False
        if isinstance(debug_value, str):
            return debug_value.lower() not in {"", "0", "false"}
        return bool(debug_value)

    def _should_hide_apps_menu(self, debug_value=None):
        if debug_value is None:
            debug_value = self.env.context.get("debug")

        if self._is_debug_mode(debug_value):
            return False

        hide_devtools = (
            self.env["ir.config_parameter"].sudo().get_param(
                "acoona_branding.hide_devtools"
            )
            or "True"
        )
        return hide_devtools.lower() in {"true", "1"}

    @api.model
    def get_user_roots(self):
        roots = super().get_user_roots()

        if not self._should_hide_apps_menu(self.env.context.get("debug")):
            return roots

        menu_ids_to_remove = []

        apps_management = self.env.ref("base.menu_management", raise_if_not_found=False)
        if apps_management:
            menu_ids_to_remove.append(apps_management.id)

        apps_menu = self.env.ref("base.menu_apps", raise_if_not_found=False)
        if apps_menu:
            menu_ids_to_remove.append(apps_menu.id)

        if not menu_ids_to_remove:
            return roots

        return roots.filtered(lambda menu: menu.id not in menu_ids_to_remove)

    @api.model
    @tools.ormcache_context("self._uid", "debug", keys=("lang",))
    def load_menus(self, debug):
        menu_self = self.with_context(debug=debug)
        menus = copy.deepcopy(super(IrUiMenu, menu_self).load_menus(debug))

        if not menu_self._should_hide_apps_menu(debug):
            return menus

        menu_ids_to_remove = set()

        apps_management = menu_self.env.ref(
            "base.menu_management", raise_if_not_found=False
        )
        if apps_management:
            menu_ids_to_remove.add(apps_management.id)

        apps_menu = menu_self.env.ref("base.menu_apps", raise_if_not_found=False)
        if apps_menu:
            menu_ids_to_remove.add(apps_menu.id)

        root_children = menus.get("root", {}).get("children", [])
        if menu_ids_to_remove & set(root_children):
            menus["root"]["children"] = [
                menu_id for menu_id in root_children if menu_id not in menu_ids_to_remove
            ]

        for menu_id in list(menu_ids_to_remove):
            menus.pop(menu_id, None)
        return menus
