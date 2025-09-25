# -*- coding: utf-8 -*-
# 本モジュールの初期化。モデル読み込みとフック公開を行います。
from . import models
from .hooks import post_init_hook  # Odoo に post_init_hook を公開
