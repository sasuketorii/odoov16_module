/** @odoo-module **/

import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

function isDebugMode(value) {
    if (value === undefined || value === null) {
        return false;
    }
    if (typeof value === "string") {
        const lowered = value.toLowerCase();
        return lowered !== "" && lowered !== "0" && lowered !== "false";
    }
    return Boolean(value);
}

patch(NavBar.prototype, "acoona_theme_should_hide_apps_menu", {
    shouldHideAppsMenu() {
        let debugEnabled = isDebugMode(session.debug);
        if (!debugEnabled && typeof window !== "undefined" && window.odoo) {
            debugEnabled = isDebugMode(window.odoo.debug);
        }
        return Boolean(session.acoona_hide_devtools) && !debugEnabled;
    },
});
