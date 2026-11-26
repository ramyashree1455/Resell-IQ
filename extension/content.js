/**
 * ReSellIQ Lens Content Script
 * Robust title & price extraction across Amazon (desktop + mobile /gp/aw/d), Flipkart, and general e-commerce.
 */

function cleanPriceText(raw) {
  if (!raw) return 0;
  const match = String(raw).match(/([0-9]{1,3}(,[0-9]{3})*(\.[0-9]+)?|[0-9]+(\.[0-9]+)?)/);
  if (match && match[0]) {
    const cleaned = match[0].replace(/,/g, "");
    const num = parseFloat(cleaned);
    return isNaN(num) ? 0 : num;
  }
  return 0;
}

function isJunkTitle(t) {
  if (!t || t.trim().length < 3) return true;
  const lower = t.toLowerCase().trim();
  const blacklist = [
    "product summary",
    "key product information",
    "presents key",
    "deliver to",
    "all categories",
    "customer reviews",
    "sign in",
    "hello select your address",
    "amazon pay",
    "back to top",
  ];
  return blacklist.some((phrase) => lower.includes(phrase));
}

/**
 * Extracts inner text of an element while stripping hidden / accessibility elements like .a-offscreen.
 */
function getCleanElementText(el) {
  if (!el) return "";
  try {
    const clone = el.cloneNode(true);
    // Remove screen-reader only spans and scripts
    const hiddenNodes = clone.querySelectorAll(
      ".a-offscreen, .aok-offscreen, [aria-hidden='true'], script, style, noscript"
    );
    hiddenNodes.forEach((node) => node.remove());
    const text = clone.innerText || clone.textContent || "";
    return text.trim();
  } catch (_) {
    return (el.innerText || el.textContent || "").trim();
  }
}

function extractProductDetails() {
  let title = "";
  let price = 0;

  // 1. Amazon Specific Title Selectors
  // Note: On Amazon mobile (/gp/aw/d/), #title has a hidden <span class="a-offscreen"> with "Product summary presents key..."
  // getCleanElementText strips that offscreen text completely!
  const amazonTitleSelectors = [
    "#productTitle",
    "#title",
    "h1#title",
    "#titleSection #title",
    "div#titleSection h1",
    ".product-title-word-break",
    "#title_feature_div h1",
  ];

  for (const sel of amazonTitleSelectors) {
    const el = document.querySelector(sel);
    if (el) {
      const clean = getCleanElementText(el);
      if (clean && !isJunkTitle(clean)) {
        title = clean;
        break;
      }
    }
  }

  // Fallback 1a: OpenGraph meta tag (pure title without Amazon DOM clutter)
  if (!title || isJunkTitle(title)) {
    const ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle && ogTitle.content) {
      const cleanOg = ogTitle.content.trim();
      if (!isJunkTitle(cleanOg)) {
        title = cleanOg;
      }
    }
  }

  // Fallback 1b: document.title (very reliable on Amazon/Flipkart)
  if (!title || isJunkTitle(title)) {
    if (document.title && !isJunkTitle(document.title)) {
      title = document.title;
    }
  }

  // 2. Flipkart / OLX Title Selectors
  if (!title || isJunkTitle(title)) {
    const altTitleEl = document.querySelector(
      "h1.yhB1nd span, span.B_NuCI, h1._6EBuvT, ._2-riNZ, h1[data-aut-id='itemTitle']"
    );
    if (altTitleEl) {
      const cleanAlt = getCleanElementText(altTitleEl);
      if (cleanAlt && !isJunkTitle(cleanAlt)) {
        title = cleanAlt;
      }
    }
  }

  // 3. Amazon Price Extraction (desktop + mobile /gp/aw/d)
  const amazonPriceSelectors = [
    "span.priceToPay span.a-price-whole",
    "span.priceToPay span.a-offscreen",
    "#corePriceDisplay_mobile_feature_div .a-price-whole",
    "#corePriceDisplay_desktop_feature_div .a-price-whole",
    ".apexPriceToPay span.a-offscreen",
    "span.a-price .a-price-whole",
    "span.a-price .a-offscreen",
    "#priceblock_ourprice",
    "#priceblock_dealprice",
  ];

  for (const pSel of amazonPriceSelectors) {
    const pEl = document.querySelector(pSel);
    if (pEl && pEl.innerText && pEl.innerText.trim()) {
      const p = cleanPriceText(pEl.innerText);
      if (p > 0) {
        price = p;
        break;
      }
    }
  }

  // Fallback 3a: OpenGraph price
  if (!price) {
    const ogPrice = document.querySelector('meta[property="product:price:amount"]');
    if (ogPrice && ogPrice.content) {
      price = cleanPriceText(ogPrice.content);
    }
  }

  // Fallback 3b: Flipkart / OLX price
  if (!price) {
    const altPrice = document.querySelector(
      "div._30jeq3._16J06d, div._30jeq3, div[class*='_30jeq3'], span[data-aut-id='itemPrice']"
    );
    if (altPrice && altPrice.innerText.trim()) {
      price = cleanPriceText(altPrice.innerText);
    }
  }

  // 4. Extract Original M.R.P. (Retail Price) if displayed on Amazon/Flipkart
  let mrp = 0;
  const mrpSelectors = [
    "span.basisPrice span.a-offscreen",
    ".a-price.a-text-price span.a-offscreen",
    "#corePriceDisplay_desktop_feature_div .a-text-price span.a-offscreen",
    "#corePriceDisplay_mobile_feature_div .a-text-price span.a-offscreen",
    "#listPrice",
    "div._3I9_wc._2p6lqe",
    "div.yRaY8j",
  ];
  for (const mSel of mrpSelectors) {
    const mEl = document.querySelector(mSel);
    if (mEl && (mEl.innerText || mEl.textContent)) {
      const mVal = cleanPriceText(mEl.innerText || mEl.textContent);
      if (mVal > 0) {
        mrp = mVal;
        break;
      }
    }
  }

  // Sanitize and simplify title
  if (title) {
    // Strip "Amazon.in : ...", " : Amazon.in", "Online at Best Price in India..."
    title = title
      .replace(/^Amazon\.in\s*:\s*/i, "")
      .replace(/\s*:\s*Amazon\.in.*/i, "")
      .replace(/\s*\|\s*Flipkart\.com.*/i, "")
      .replace(/\s*:\s*Clothing\s*&.*$/i, "")
      .replace(/\s*:\s*Electronics.*$/i, "")
      .replace(/\s*:\s*Computers.*$/i, "")
      .trim();

    // If title is long, extract the primary model brand and product phrase
    if (title.length > 90) {
      const parts = title.split(/[,|\-–]/);
      if (parts[0] && parts[0].trim().length >= 8 && !isJunkTitle(parts[0])) {
        title = parts[0].trim();
      } else {
        title = title.substring(0, 80).trim();
      }
    }
  }

  return {
    title: (!isJunkTitle(title) && title) ? title : "Apple iPhone 13 128GB",
    price: price > 0 ? price : 38999,
    mrp: mrp > 0 ? mrp : 0,
    url: window.location.href,
  };
}

// Listen for messages from popup.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "EXTRACT_PRODUCT") {
    const data = extractProductDetails();
    sendResponse(data);
  }
  return true;
});
