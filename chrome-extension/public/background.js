chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    // Pass everything to native host
    // if (msg.action !== "organize_tabs") return;

    // Add openedAt timestamp to each tab if organizing
    if (msg.action === "organize_tabs" && Array.isArray(msg.tabs)) {
        const now = Date.now();
        msg.tabs = msg.tabs.map(tab => ({
            ...tab,
            openedAt: now
        }));
    }

    let responded = false;

    // ✅ CORRECT native host name
    const port = chrome.runtime.connectNative("ai.tab.manager");

    port.onMessage.addListener((message) => {
        responded = true;

        // native host sends { ok, data }
        sendResponse(message);
    });

    port.onDisconnect.addListener(() => {
        if (!responded) {
            const err = chrome.runtime.lastError;
            if (err) {
                console.error("Native host error:", err.message);
            }
        }
        // ❌ do NOT log anything on normal disconnect
    });

    port.postMessage(msg);

    // 🔒 REQUIRED for async response in MV3
    return true;
});
