/** @odoo-module **/

const FAVICON_PATH = "/acoona_theme/static/src/img/ACOONA-A.png";
const BRAND_NAME = "Acoona";

/**
 * フロントエンド（ログインページなど）のブランディングを適用する
 */
function applyBranding() {
  // タイトルを変更
  document.title = BRAND_NAME;

  // キャッシュバスティング用のタイムスタンプ
  const timestamp = Date.now();
  const faviconUrl = `${FAVICON_PATH}?v=${timestamp}`;

  console.log("[Acoona Frontend] Applying favicon:", faviconUrl);

  // 既存のファビコン関連タグをすべて削除
  const existingIcons = document.querySelectorAll(
    'link[rel*="icon"], link[rel="apple-touch-icon"]'
  );
  console.log(
    "[Acoona Frontend] Removing existing icons:",
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

  // MSタイルイメージを変更
  const msTileSelector = "meta[name='msapplication-TileImage']";
  let msTile = document.querySelector(msTileSelector);
  if (!msTile) {
    msTile = document.createElement("meta");
    msTile.name = "msapplication-TileImage";
    document.head.appendChild(msTile);
  }
  msTile.setAttribute("content", faviconUrl);

  // ブラウザに強制的に再読み込みさせる技法
  const tempLink = document.createElement("link");
  tempLink.rel = "icon";
  tempLink.href = "data:,";
  document.head.appendChild(tempLink);
  setTimeout(() => {
    tempLink.remove();
    // 再度Acoonaファビコンを追加
    const finalIcon = document.createElement("link");
    finalIcon.rel = "icon";
    finalIcon.type = "image/png";
    finalIcon.href = faviconUrl;
    finalIcon.setAttribute("data-acoona-favicon", "true");
    document.head.appendChild(finalIcon);
  }, 50);

  // タイトルの監視と強制更新
  const titleObserver = new MutationObserver(() => {
    if (document.title !== BRAND_NAME) {
      document.title = BRAND_NAME;
    }
  });

  titleObserver.observe(
    document.querySelector("title") || document.head,
    {
      childList: true,
      subtree: true,
      characterData: true,
    }
  );

  // ファビコンの定期監視
  setInterval(() => {
    const currentIcons = document.querySelectorAll('link[rel*="icon"]');
    let hasAcoonaIcon = false;
    currentIcons.forEach((icon) => {
      if (icon.href.includes("ACOONA-A.png")) {
        hasAcoonaIcon = true;
      }
    });
    if (!hasAcoonaIcon) {
      console.log("[Acoona Frontend] Re-applying favicon");
      applyBranding();
    }
  }, 2000);

  console.log("[Acoona Frontend] Branding applied successfully");
}

// DOM読み込み時に適用
document.addEventListener("DOMContentLoaded", applyBranding, { once: true });

// 即座に実行も試みる（DOMContentLoadedが既に発火している場合）
const isReady =
  document.readyState === "interactive" ||
  document.readyState === "complete";
if (isReady) {
  applyBranding();
}
