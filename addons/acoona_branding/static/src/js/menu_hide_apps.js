/** @odoo-module **/

import { menuService } from "@web/webclient/menus/menu_service";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

const APPS_MENU_XMLID = "base.menu_apps";

patch(menuService, "acoona_branding_hide_apps_menu", {
    async start(env) {
        const menus = await this._super(env);
        const shouldHideApps = Boolean(session.acoona_hide_devtools) && !session.debug;

        if (!shouldHideApps) {
            return menus;
        }

        const originalGetApps = menus.getApps.bind(menus);
        const originalSelectMenu = menus.selectMenu.bind(menus);

        const allApps = originalGetApps();
        const appsMenu = allApps.find((app) => app.xmlid === APPS_MENU_XMLID);
        const filteredApps = allApps.filter((app) => app.xmlid !== APPS_MENU_XMLID);

        menus.getApps = (...args) => {
            if (args.length) {
                return originalGetApps(...args).filter(
                    (app) => app.xmlid !== APPS_MENU_XMLID
                );
            }
            return filteredApps;
        };

        if (appsMenu) {
            const rootMenu = menus.getMenu("root");
            if (rootMenu) {
                rootMenu.children = rootMenu.children.filter(
                    (id) => id !== appsMenu.id
                );
                delete rootMenu.childrenTree;
            }

            const currentApp = menus.getCurrentApp && menus.getCurrentApp();
            if (currentApp && currentApp.id === appsMenu.id) {
                const fallbackApp = filteredApps[0];
                if (fallbackApp) {
                    await originalSelectMenu(fallbackApp);
                }
            }

            menus.selectMenu = async (menu) => {
                const menuRecord =
                    typeof menu === "number" ? menus.getMenu(menu) : menu;
                if (menuRecord?.xmlid === APPS_MENU_XMLID) {
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
