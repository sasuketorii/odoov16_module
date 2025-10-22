"""acoona_l10n_jp_invoice_system
Odoo 16 のドキュメントレイアウトに「Japan」を追加し、
請求書レイアウトを日本仕様にカスタマイズします。
"""

from . import models
from .hooks import post_init_hook, uninstall_hook

__all__ = [
    "post_init_hook",
    "uninstall_hook",
]
