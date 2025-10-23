/** @odoo-module **/

import { menuService } from "@web/webclient/menus/menu_service";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

const HIDE_MENU_XMLIDS = ["base.menu_apps", "base.menu_management"];

function isDebugValue(value) {
    if (value === undefined || value === null) {
        return false;
    }
    if (typeof value === "string") {
        const lowered = value.toLowerCase();
        return lowered !== "" && lowered !== "0" && lowered !== "false";
    }
    return Boolean(value);
}

function isDebugEnabled() {
    if (isDebugValue(session.debug)) {
        return true;
    }
    const globalDebug =
        (typeof window !== "undefined" && window.odoo && window.odoo.debug) || false;
    return isDebugValue(globalDebug);
}

patch(menuService, "acoona_branding_hide_apps_menu", {
    async start(env) {
        const menus = await this._super(env);
        const shouldHideApps =
            Boolean(session.acoona_hide_devtools) && !isDebugEnabled();
        console.log(
            "[Acoona Branding] menu patch",
            "session.debug=",
            session.debug,
            "shouldHideApps=",
            shouldHideApps
        );

        if (!shouldHideApps) {
            return menus;
        }

        const originalGetApps = menus.getApps.bind(menus);
        const originalSelectMenu = menus.selectMenu.bind(menus);

        const allApps = originalGetApps();
        const hiddenApps = allApps.filter((app) => HIDE_MENU_XMLIDS.includes(app.xmlid));
        const filteredApps = allApps.filter((app) => !HIDE_MENU_XMLIDS.includes(app.xmlid));

        menus.getApps = (...args) => {
            if (args.length) {
                return originalGetApps(...args).filter(
                    (app) => !HIDE_MENU_XMLIDS.includes(app.xmlid)
                );
            }
            return filteredApps;
        };

        if (hiddenApps.length) {
            const rootMenu = menus.getMenu("root");
            if (rootMenu) {
                rootMenu.children = rootMenu.children.filter(
                    (id) =>
                        !hiddenApps.some((appMenu) => appMenu.id === id)
                );
                delete rootMenu.childrenTree;
            }

            const currentApp = menus.getCurrentApp && menus.getCurrentApp();
            if (
                currentApp &&
                hiddenApps.some((appMenu) => appMenu.id === currentApp.id)
            ) {
                const fallbackApp = filteredApps[0];
                if (fallbackApp) {
                    await originalSelectMenu(fallbackApp);
                }
            }

            menus.selectMenu = async (menu) => {
                const menuRecord =
                    typeof menu === "number" ? menus.getMenu(menu) : menu;
                if (
                    menuRecord?.xmlid &&
                    HIDE_MENU_XMLIDS.includes(menuRecord.xmlid)
                ) {
                    const fallbackApp = filteredApps[0];
                    if (fallbackApp) {
                        return originalSelectMenu(fallbackApp);
                    }
                    return;
                }
                return originalSelectMenu(menu);
            };
        }

        return menus;
    },
});
