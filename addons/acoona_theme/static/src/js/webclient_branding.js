/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";

const FAVICON_PATH = "/acoona_theme/static/src/img/ACOONA-A.png";
const BRAND_NAME = "Acoona";
const BRAND_REPLACEMENTS = [
  { regex: /\bOdoo(\s+S\.A\.)?\b/g, replacement: BRAND_NAME },
];
const ATTRIBUTE_SKIP_TAGS = new Set(["SCRIPT", "STYLE", "LINK", "META"]);
const TEXT_SKIP_TAGS = new Set(["SCRIPT", "STYLE", "CODE", "PRE", "TEXTAREA"]);

/**
 * ファビコンを強制的に変更する
 * 既存のファビコンタグをすべて削除してから新しいものを追加
 */
function applyBrandingFavicon() {
  // キャッシュバスティング用のタイムスタンプ
  const timestamp = Date.now();
  const faviconUrl = `${FAVICON_PATH}?v=${timestamp}`;

  console.log("[Acoona Branding] Applying favicon:", faviconUrl);

  // 既存のファビコン関連タグをすべて削除
  const existingIcons = document.querySelectorAll(
    'link[rel*="icon"], link[rel="apple-touch-icon"]'
  );
  console.log(
    "[Acoona Branding] Removing existing icons:",
    existingIcons.length
  );
  existingIcons.forEach((icon) => icon.remove());

  // 新しいファビコンタグを作成
  const faviconConfigs = [
    { rel: "icon", type: "image/png", sizes: "16x16" },
    { rel: "icon", type: "image/png", sizes: "32x32" },
    { rel: "shortcut icon", type: "image/png" },
    { rel: "apple-touch-icon", sizes: "180x180" },
    { rel: "icon", sizes: "192x192" },
  ];

  faviconConfigs.forEach((config) => {
    const link = document.createElement("link");
    link.rel = config.rel;
    link.href = faviconUrl;
    link.setAttribute("data-acoona-favicon", "true");
    if (config.type) link.type = config.type;
    if (config.sizes) link.sizes = config.sizes;
    document.head.appendChild(link);
  });

  // MSタイルイメージ
  let msTile = document.querySelector(
    "meta[name='msapplication-TileImage']"
  );
  if (!msTile) {
    msTile = document.createElement("meta");
    msTile.name = "msapplication-TileImage";
    document.head.appendChild(msTile);
  }
  msTile.setAttribute("content", faviconUrl);

  // ブラウザに強制的に再読み込みさせる技法
  // 1. 一時的に空のファビコンを設定
  const tempLink = document.createElement("link");
  tempLink.rel = "icon";
  tempLink.href = "data:,";
  document.head.appendChild(tempLink);
  setTimeout(() => {
    tempLink.remove();
    // 2. 再度Acoonaファビコンを追加
    const finalIcon = document.createElement("link");
    finalIcon.rel = "icon";
    finalIcon.type = "image/png";
    finalIcon.href = faviconUrl;
    finalIcon.setAttribute("data-acoona-favicon", "true");
    document.head.appendChild(finalIcon);
  }, 50);

  console.log("[Acoona Branding] Favicon applied successfully");
}

function replaceBrandingInText(node) {
  let value = node.nodeValue;
  if (!value) {
    return;
  }
  let updated = value;
  BRAND_REPLACEMENTS.forEach(({ regex, replacement }) => {
    updated = updated.replace(regex, replacement);
  });
  if (updated !== value) {
    node.nodeValue = updated;
  }
}

function replaceBrandingInAttributes(element) {
  if (!element || ATTRIBUTE_SKIP_TAGS.has(element.tagName)) {
    return;
  }
  for (const attr of Array.from(element.attributes || [])) {
    const value = attr.value;
    if (!value) {
      continue;
    }
    let updated = value;
    BRAND_REPLACEMENTS.forEach(({ regex, replacement }) => {
      updated = updated.replace(regex, replacement);
    });
    if (updated !== value) {
      element.setAttribute(attr.name, updated);
    }
  }
}

function applyBrandingToElement(element) {
  if (!element) {
    return;
  }
  if (element.nodeType === Node.TEXT_NODE) {
    if (
      element.parentElement &&
      !TEXT_SKIP_TAGS.has(element.parentElement.tagName)
    ) {
      replaceBrandingInText(element);
    }
    return;
  }

  replaceBrandingInAttributes(element);

  const walker = document.createTreeWalker(
    element,
    NodeFilter.SHOW_TEXT,
    null,
    false
  );
  let current;
  while ((current = walker.nextNode())) {
    if (
      current.parentElement &&
      !TEXT_SKIP_TAGS.has(current.parentElement.tagName)
    ) {
      replaceBrandingInText(current);
    }
  }
}

function observeBrandingMutations() {
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === "childList") {
        mutation.addedNodes.forEach((node) => {
          applyBrandingToElement(node);
        });
      } else if (mutation.type === "attributes") {
        replaceBrandingInAttributes(mutation.target);
      }
    }
  });
  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
  });
  return observer;
}

/**
 * タイトルサービスをカスタマイズ
 */
const acoonaTitleService = {
  dependencies: [],
  start() {
    let parts = { zopenerp: BRAND_NAME };
    const title = {
      get current() {
        const suffix = parts.zopenerp ? ` - ${parts.zopenerp}` : "";
        return (
          Object.keys(parts)
            .filter((k) => k !== "zopenerp")
            .map((k) => parts[k])
            .join(" - ") + suffix
        );
      },
      setParts(newParts) {
        parts = Object.assign({}, parts, newParts);
        parts.zopenerp = BRAND_NAME;
        document.title = this.current;
      },
    };
    document.title = title.current;
    return title;
  },
};

// タイトルサービスを置き換え
const serviceRegistry = registry.category("services");
serviceRegistry.remove("title");
serviceRegistry.add("title", acoonaTitleService, { force: true });

/**
 * WebClientをパッチしてブランディングを適用
 */
patch(WebClient.prototype, "acoona_theme.webclient_branding", {
  setup() {
    this._super(...arguments);
    
    // 初回実行
    applyBrandingFavicon();
    applyBrandingToElement(document.body);
    observeBrandingMutations();
    
    // タイトルとファビコンを定期的に監視して強制更新
    setInterval(() => {
      // タイトルの監視
      const isNotBranded =
        document.title !== BRAND_NAME &&
        !document.title.startsWith(BRAND_NAME);
      if (isNotBranded && this.title) {
        this.title.setParts({ zopenerp: BRAND_NAME });
      }
      
      // ファビコンの監視と強制更新
      const currentIcons = document.querySelectorAll(
        'link[rel*="icon"]'
      );
      let hasAcoonaIcon = false;
      currentIcons.forEach((icon) => {
        if (icon.href.includes("ACOONA-A.png")) {
          hasAcoonaIcon = true;
        }
      });
      
      // Acoonaのファビコンがない場合は再適用
      if (!hasAcoonaIcon) {
        applyBrandingFavicon();
      }
    }, 1000);
  },
});
