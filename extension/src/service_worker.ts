const OFFSCREEN_PATH = 'offscreen.html';

async function ensureOffscreenDocument(): Promise<void> {
  if (await chrome.offscreen.hasDocument?.()) {
    return;
  }

  try {
    await chrome.offscreen.createDocument({
      url: OFFSCREEN_PATH,
      reasons: ['WORKERS'],
      justification: 'Persistent WebSocket connection to local MCP server',
    });
    console.log('[SW] Offscreen document created');
  } catch (err: any) {
    if (!err.message?.includes('Only a single offscreen')) {
      throw err;
    }
  }
}

chrome.runtime.onStartup.addListener(ensureOffscreenDocument);
chrome.runtime.onInstalled.addListener(ensureOffscreenDocument);

ensureOffscreenDocument();

// ─── Tab tracking (decoupled from focus) ──────────────────────────────────

let lastActiveTabId: number | null = null;

chrome.tabs.onActivated.addListener(({ tabId }) => {
  lastActiveTabId = tabId;
});

chrome.tabs.onRemoved.addListener((tabId) => {
  if (lastActiveTabId === tabId) {
    lastActiveTabId = null;
  }
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.source !== 'offscreen' || message.type !== 'command') {
    return false;
  }

  const request = message.payload;

  if (request.type === 'click') {
    handleClick(request.payload.selector)
      .then((result) => sendResponse({ ok: true, result }))
      .catch((err) =>
        sendResponse({ ok: false, error: { code: 'EXEC_ERROR', message: String(err) } })
      );
    return true;
  }

  sendResponse({ ok: false, error: { code: 'UNKNOWN_TYPE', message: request.type } });
  return false;
});

// TODO: add read-only commands (screenshot, DOM snapshot) so LLM can verify page state
// TODO: add MCP tool descriptions that tell LLM to wait/check state after actions
//
// NOTE: For reliable LLM-driven testing, we likely need:
//   - getUrl / getTitle - verify navigation after click
//   - getDom / getVisibleElements - return interactive elements only (not full HTML noise)
//   - screenshot - visual verification (requires CDP / chrome.debugger in Phase 3)
//   - explicit wait command - Playwright has auto-waiting, our bridge does not
//
// ARCHITECTURE IDEA: Two MCP modes:
//   1. Explore mode - LLM uses our bridge (click, getDom, etc) to discover the app
//   2. Generate mode - LLM writes Playwright tests directly, no bridge needed
//   Workflow: Explore → understand → Generate .spec.ts files

async function handleClick(selector: string): Promise<unknown> {
  if (lastActiveTabId === null) {
    throw new Error('No active tab recorded. Please switch to a tab first.');
  }

  const results = await chrome.scripting.executeScript({
    target: { tabId: lastActiveTabId },
    func: (sel: string) => {
      // TODO: consider querySelectorAll and click all matches, or add an index param
      const el = document.querySelector(sel);
      if (!el) throw new Error(`Element not found: ${sel}`);
      (el as HTMLElement).click();
      return { clicked: true, selector: sel };
    },
    args: [selector],
  });

  const frameResult = results[0] as { result?: unknown; error?: unknown };
  if (frameResult.error) throw frameResult.error;
  return frameResult.result;
}
