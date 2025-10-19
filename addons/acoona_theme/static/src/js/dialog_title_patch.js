odoo.define('acoona_theme.DialogTitlePatch', function (require) {
    'use strict';

    const Dialog = require('web.Dialog');
    const core = require('web.core');
    const _t = core._t;

    const ODOO_LABEL_REGEX = /\bOdoo\b/g;

    function toAcoona(value) {
        if (typeof value !== 'string') {
            return value;
        }
        return value.replace(ODOO_LABEL_REGEX, _t('Acoona'));
    }

    Dialog.include({
        init(parent, options) {
            options = options || {};
            options.title = toAcoona(options.title) || _t('Acoona');
            options.subtitle = toAcoona(options.subtitle);
            return this._super.apply(this, arguments);
        },
        setTitle(title) {
            return this._super(toAcoona(title));
        },
    });
});
