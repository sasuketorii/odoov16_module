# -*- coding: utf-8 -*-
"""report_layout_guard
外部帳票レイアウト参照が常に ir.ui.view を指すよう強制するアドオン。
"""

from . import hooks  # noqa: F401
from . import models  # noqa: F401


def post_init_hook(cr, registry):
    hooks.post_init_hook(cr, registry)


def uninstall_hook(cr, registry):
    hooks.uninstall_hook(cr, registry)
