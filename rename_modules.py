#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 内のモジュール技術名を一括でリネームし、関連レコードを整合させるユーティリティ。

使用例:
    docker compose exec odoo python /mnt/extra-addons/rename_modules.py
必要に応じて接続情報を引数で上書きできます (--db-name 等)。
"""

import argparse
import logging
import sys

import odoo
from odoo import SUPERUSER_ID, api
from odoo.modules.registry import Registry
from odoo.tools import config as odoo_config

# 旧 -> 新 技術名マッピング
MODULE_RENAMES = [
    ("acoona_branding2", "acoona_branding"),
    ("jp_bank_account_minimal", "acoona_jp_bank"),
    ("l10n_jp_address_layout", "acoona_l10n_jp_address_layout"),
    ("l10n_jp_invoice_system", "acoona_l10n_jp_invoice_system"),
    ("report_layout_guard", "acoona_report_layout_guard"),
    ("discuss_customization", "acoona_discus"),
]


def parse_args():
    parser = argparse.ArgumentParser(description="Rename Odoo module technical names in DB.")
    parser.add_argument("--db-name", default="odoo", help="Database name (default: odoo)")
    parser.add_argument("--db-user", default="odoo", help="Database user (default: odoo)")
    parser.add_argument("--db-password", default="odoo", help="Database password (default: odoo)")
    parser.add_argument("--db-host", default="db", help="Database host (default: db)")
    parser.add_argument("--db-port", default="5432", help="Database port (default: 5432)")
    parser.add_argument(
        "--addons-path",
        default="/mnt/extra-addons",
        help="Addons path for module scanning (default: /mnt/extra-addons)",
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase log verbosity (repeatable)"
    )
    return parser.parse_args()


def configure_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def bootstrap_odoo(args) -> None:
    odoo_config.parse_config(
        [
            f"--database={args.db_name}",
            f"--db_user={args.db_user}",
            f"--db_password={args.db_password}",
            f"--db_host={args.db_host}",
            f"--db_port={args.db_port}",
            f"--addons-path={args.addons_path}",
        ]
    )


def rename_config_parameters(env, old, new):
    ICP = env["ir.config_parameter"].sudo()
    params = ICP.search([("key", "ilike", f"%{old}%")])
    renamed = 0
    for param in params:
        key = param.key or ""
        if old not in key:
            continue
        new_key = key.replace(old, new, 1)
        if new_key == key:
            continue
        if ICP.search_count([("key", "=", new_key)]):
            logging.warning("Config key %s already exists, skipping merge into %s", new_key, key)
            continue
        param.write({"key": new_key})
        renamed += 1
    if renamed:
        logging.info("Renamed %s config parameters from %s to %s", renamed, old, new)


def rename_module_records(env, old, new):
    Module = env["ir.module.module"].sudo()
    mod_old = Module.search([("name", "=", old)], limit=1)
    mod_new = Module.search([("name", "=", new)], limit=1)

    if not mod_old and not mod_new:
        logging.info("No module records for %s or %s; skipping", old, new)
        return

    if mod_new and mod_old:
        if mod_new.state not in ("installed", "to upgrade", "to install"):
            logging.info("Removing duplicate module entry %s (state=%s)", new, mod_new.state)
            mod_new.unlink()
            mod_new = Module.browse()
        else:
            logging.info("Module %s already present with state=%s; skipping rename", new, mod_new.state)
            return

    if mod_old:
        env.cr.execute(
            "UPDATE ir_module_module SET name=%s WHERE name=%s",
            (new, old),
        )
        logging.info("Renamed ir.module.module entry %s -> %s", old, new)

    # Dependencies (char field)
    env.cr.execute(
        "UPDATE ir_module_module_dependency SET name=%s WHERE name=%s",
        (new, old),
    )


def rename_generic_module_fields(env, old, new):
    Fields = env["ir.model.fields"].sudo()
    module_field_defs = Fields.search(
        [
            ("name", "=", "module"),
            ("ttype", "in", ("char", "text", "selection")),
            ("store", "=", True),
        ]
    )
    for field in module_field_defs:
        Model = env[field.model].sudo().with_context(active_test=False)
        try:
            records = Model.search([(field.name, "=", old)])
        except Exception as exc:  # pylint: disable=broad-except
            logging.debug("Skipping %s.%s: %s", field.model, field.name, exc)
            continue
        if records:
            records.write({field.name: new})
            logging.info("Updated %d rows in %s.%s", len(records), field.model, field.name)

    modules_field_defs = Fields.search(
        [
            ("name", "=", "modules"),
            ("ttype", "in", ("char", "text")),
            ("store", "=", True),
        ]
    )
    for field in modules_field_defs:
        Model = env[field.model].sudo().with_context(active_test=False)
        try:
            records = Model.search([(field.name, "ilike", f"%{old}%")])
        except Exception as exc:  # pylint: disable=broad-except
            logging.debug("Skipping %s.%s: %s", field.model, field.name, exc)
            continue
        for rec in records:
            value = rec[field.name] or ""
            parts = [chunk.strip() for chunk in value.split(",") if chunk.strip()]
            replaced = False
            for idx, chunk in enumerate(parts):
                if chunk == old:
                    parts[idx] = new
                    replaced = True
            if replaced:
                rec[field.name] = ",".join(parts)


def rename_model_data(env, old, new):
    ModelData = env["ir.model.data"].sudo().with_context(active_test=False)
    records = ModelData.search([("module", "=", old)])
    if records:
        records.write({"module": new})
        logging.info("Updated %d ir.model.data rows for %s -> %s", len(records), old, new)

    if "ir.translation" in env:
        Translation = env["ir.translation"].sudo()
        translations = Translation.search([("module", "=", old)])
        if translations:
            translations.write({"module": new})
            logging.info(
                "Updated %d ir.translation rows for %s -> %s",
                len(translations),
                old,
                new,
            )


def rename_view_keys(env, old, new):
    View = env["ir.ui.view"].sudo().with_context(active_test=False)
    views = View.search([("key", "like", f"{old}.%")])
    for view in views:
        key = view.key or ""
        if key.startswith(f"{old}."):
            view.key = f"{new}.{key.split('.', 1)[1]}"


def rename_reports(env, old, new):
    Report = env["ir.actions.report"].sudo().with_context(active_test=False)
    for field in ("report_name", "report_file"):
        reports = Report.search([(field, "like", f"{old}.%")])
        for rec in reports:
            value = getattr(rec, field) or ""
            if value.startswith(f"{old}."):
                setattr(rec, field, f"{new}.{value.split('.', 1)[1]}")


def rename_misc_tables(env, old, new):
    # Config parameters
    rename_config_parameters(env, old, new)
    # Generic module fields and ir.model/fields metadata
    rename_generic_module_fields(env, old, new)
    # ir.model.data / translations
    rename_model_data(env, old, new)
    # View keys and report identifiers
    rename_view_keys(env, old, new)
    rename_reports(env, old, new)


def upgrade_modules(env):
    Module = env["ir.module.module"].sudo()
    Module.update_list()
    for _old, new in MODULE_RENAMES:
        module = Module.search([("name", "=", new)], limit=1)
        if not module:
            logging.warning("Module %s not found after rename; skip upgrade", new)
            continue
        state = module.state
        if state == "installed":
            logging.info("Upgrading module %s", new)
            module.button_immediate_upgrade()
        elif state in ("to install", "uninstalled"):
            logging.info("Installing module %s", new)
            module.button_immediate_install()
        elif state in ("to upgrade",):
            logging.info("Module %s already marked to upgrade", new)
            module.button_immediate_upgrade()
        else:
            logging.info("Module %s in state %s; skipping automatic upgrade", new, state)


def run(env):
    for old, new in MODULE_RENAMES:
        logging.info("Processing rename %s -> %s", old, new)
        rename_module_records(env, old, new)
        rename_misc_tables(env, old, new)
    upgrade_modules(env)


def main():
    args = parse_args()
    configure_logging(args.verbose)
    bootstrap_odoo(args)

    try:
        registry = Registry.new(args.db_name)
    except Exception:  # pylint: disable=broad-except
        logging.exception("Failed to initialize Odoo registry")
        sys.exit(1)

    with api.Environment.manage():
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            try:
                run(env)
            except Exception:  # pylint: disable=broad-except
                logging.exception("Module rename procedure failed")
                cr.rollback()
                sys.exit(1)
            else:
                cr.commit()
                logging.info("Module rename completed successfully")


if __name__ == "__main__":
    main()
