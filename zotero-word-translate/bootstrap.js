const PLUGIN_ID = "word-translate@example.com";
const EVENT_TYPE = "renderTextSelectionPopup";
const MAX_TEXT_LENGTH = 200;

let selectionHandler;
let translationCache = new Map();

function log(message, error) {
  Zotero.debug(`[Zotero 选词翻译] ${message}`);
  if (error) {
    Zotero.logError(error);
  }
}

function install() {
  log("插件已安装");
}

async function startup() {
  await Zotero.initializationPromise;

  selectionHandler = event => {
    void renderTranslation(event);
  };

  Zotero.Reader.registerEventListener(
    EVENT_TYPE,
    selectionHandler,
    PLUGIN_ID
  );

  log("插件已启动");
}

function shutdown() {
  if (selectionHandler) {
    Zotero.Reader.unregisterEventListener(EVENT_TYPE, selectionHandler);
  }
  selectionHandler = undefined;
  translationCache.clear();
  log("插件已停止");
}

function uninstall() {
  log("插件已卸载");
}

async function renderTranslation({ doc, params, append }) {
  const text = normalizeSelection(params?.annotation?.text || "");
  const card = createCard(doc, text);
  append(card.root);

  if (!text) {
    card.setStatus("请选中一个单词");
    return;
  }

  if (text.length > MAX_TEXT_LENGTH) {
    card.setStatus(`选中的内容过长（最多 ${MAX_TEXT_LENGTH} 个字符）`);
    return;
  }

  try {
    card.setStatus("翻译中…", true);
    const translation = await translate(text);

    // The popup may have been removed while the request was in flight.
    if (!card.root.isConnected) return;
    card.setTranslation(translation);
  }
  catch (error) {
    if (!card.root.isConnected) return;
    card.setStatus(humanizeError(error));
    // Do not persist the user's selected text in Zotero diagnostic logs.
    log("翻译失败", error);
  }
}

function normalizeSelection(value) {
  return value
    .replace(/\u00ad/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/^[\s"“”'‘’()[\]{}<>.,;:!?，。；：！？、]+/, "")
    .replace(/[\s"“”'‘’()[\]{}<>.,;:!?，。；：！？、]+$/, "");
}

function createCard(doc, sourceText) {
  const root = doc.createElement("div");
  root.setAttribute("role", "status");
  root.style.cssText = [
    "min-width: 210px",
    "max-width: 320px",
    "padding: 10px 12px",
    "margin: 4px 2px",
    "border-left: 3px solid #4f7cac",
    "border-radius: 6px",
    "background: color-mix(in srgb, Canvas 94%, #4f7cac 6%)",
    "color: CanvasText",
    "font: 13px/1.45 system-ui, sans-serif",
    "overflow-wrap: anywhere"
  ].join(";");

  const source = doc.createElement("div");
  source.textContent = sourceText || "选词翻译";
  source.style.cssText = [
    "font-size: 12px",
    "font-weight: 600",
    "opacity: .68",
    "margin-bottom: 4px"
  ].join(";");

  const result = doc.createElement("div");
  result.style.cssText = "font-size: 15px; user-select: text";

  const note = doc.createElement("div");
  note.textContent = "由 MyMemory 在线翻译";
  note.style.cssText = [
    "font-size: 10px",
    "opacity: .48",
    "margin-top: 5px"
  ].join(";");

  root.append(source, result, note);

  return {
    root,
    setStatus(message, loading = false) {
      result.textContent = message;
      result.style.opacity = loading ? ".6" : ".82";
      note.hidden = true;
    },
    setTranslation(message) {
      result.textContent = message;
      result.style.opacity = "1";
      note.hidden = false;
    }
  };
}

async function translate(text) {
  const containsChinese = /[\u3400-\u9fff]/.test(text);
  const sourceLanguage = containsChinese ? "zh-CN" : "en";
  const targetLanguage = containsChinese ? "en" : "zh-CN";
  const cacheKey = `${sourceLanguage}:${targetLanguage}:${text.toLocaleLowerCase()}`;

  if (translationCache.has(cacheKey)) {
    return translationCache.get(cacheKey);
  }

  const url = "https://api.mymemory.translated.net/get"
    + `?q=${encodeURIComponent(text)}`
    + `&langpair=${encodeURIComponent(`${sourceLanguage}|${targetLanguage}`)}`;

  const request = await Zotero.HTTP.request("GET", url, {
    responseType: "json",
    timeout: 12000
  });

  const payload = typeof request.response === "string"
    ? JSON.parse(request.response)
    : request.response;

  if (Number(payload?.responseStatus) !== 200) {
    throw new Error(payload?.responseDetails || "翻译服务返回错误");
  }

  const translatedText = payload?.responseData?.translatedText?.trim();
  if (!translatedText) {
    throw new Error("没有找到翻译结果");
  }

  remember(cacheKey, translatedText);
  return translatedText;
}

function remember(key, value) {
  if (translationCache.size >= 300) {
    const oldestKey = translationCache.keys().next().value;
    translationCache.delete(oldestKey);
  }
  translationCache.set(key, value);
}

function humanizeError(error) {
  const message = String(error?.message || error || "");
  if (/timeout/i.test(message)) return "翻译超时，请稍后重试";
  if (/429|quota|limit/i.test(message)) return "今日免费翻译额度已用完";
  return "暂时无法翻译，请检查网络后重试";
}
