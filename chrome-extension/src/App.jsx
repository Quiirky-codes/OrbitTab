import { useState, useEffect } from "react";
import TabGroup from "./components/TabGroup";

const BLOCKED_DOMAIN_KEYWORDS = [
    "bank",
    "auth",
    "signin",
    "payment",
    "wallet",
    "account"
];

export default function App() {
    const [groups, setGroups] = useState(null);
    const [loading, setLoading] = useState(false);
    const [recentSessions, setRecentSessions] = useState([]);
    const [pinnedTabIds, setPinnedTabIds] = useState(new Set());

    useEffect(() => {
        // Load pinned tabs
        chrome.storage.local.get(["pinnedTabIds"], (result) => {
            if (!chrome.runtime.lastError && result?.pinnedTabIds) {
                setPinnedTabIds(new Set(result.pinnedTabIds));
            }
        });

        fetchRecentSessions();

        // Keyboard shortcut: Cmd/Ctrl + Shift + O
        const handleKeyDown = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key.toLowerCase() === "o") {
                e.preventDefault();
                organizeTabs();
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, []);

    async function fetchRecentSessions() {
        try {
            const response = await chrome.runtime.sendMessage({
                action: "get_recent_sessions" // must match backend
            });

            if (response && response.ok && Array.isArray(response.data)) {
                setRecentSessions(response.data);
            }
        } catch (err) {
            console.error("Error fetching sessions:", err);
        }
    }

    async function organizeTabs() {
        setLoading(true);
        setGroups(null);

        try {
            const tabs = await chrome.tabs.query({});

            // 🔒 Exclude pinned tabs
            const filteredTabs = tabs.filter(t => !pinnedTabIds.has(t.id));

            // 🔒 Remove sensitive domains + minimize data
            const safeTabs = filteredTabs
                .filter(t => {
                    try {
                        const hostname = new URL(t.url).hostname;
                        return !BLOCKED_DOMAIN_KEYWORDS.some(keyword =>
                            hostname.includes(keyword)
                        );
                    } catch {
                        return false;
                    }
                })
                .map(t => {
                    const hostname = new URL(t.url).hostname;

                    return {
                        title: t.title,
                        domain: hostname,   // 🔒 Only hostname, not full URL
                        tabId: t.id
                    };
                });

            const result = await chrome.runtime.sendMessage({
                action: "organize_tabs",
                tabs: safeTabs
            });

            if (result?.ok === false) {
                console.error("Native host error:", result.error);
                setLoading(false);
                return;
            }

            setGroups(result.data || []);
            fetchRecentSessions();

        } catch (err) {
            console.error("Error organizing tabs:", err);
        }

        setLoading(false);
    }

    function togglePin(tabId) {
        const newPinned = new Set(pinnedTabIds);

        if (newPinned.has(tabId)) {
            newPinned.delete(tabId);
        } else {
            newPinned.add(tabId);
        }

        setPinnedTabIds(newPinned);
        chrome.storage.local.set({
            pinnedTabIds: Array.from(newPinned)
        });
    }

    function exportSession(format) {
        if (!groups) return;

        let content = "";

        groups.forEach(g => {
            if (format === "markdown") {
                content += `### ${g.name}\n`;
                g.tabs.forEach(t => {
                    content += `- ${t.title}\n  ${t.summary}\n\n`;
                });
            } else {
                content += `${g.name}\n`;
                g.tabs.forEach(t => {
                    content += `  - ${t.title}\n    ${t.summary}\n`;
                });
                content += "\n";
            }
        });

        const blob = new Blob([content], { type: "text/plain" });
        const fileUrl = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = fileUrl;
        a.download = `orbitab_session_${new Date().toISOString()}.${format === "markdown" ? "md" : "txt"
            }`;

        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    return (
        <div className="container">

            {/* Header */}
            <div className="header">
                <img
                    src="/assets/OrbitTab_logo.png"
                    alt="OrbiTab logo"
                    className="logo"
                />
                <h1>ORBIT TAB</h1>
                <span>Your AI-powered tab manager</span>
                <div className="privacy-badge">
                    100% Local. No data leaves your device.
                </div>
            </div>

            {/* Primary Action */}
            <button
                className="button"
                onClick={organizeTabs}
                disabled={loading}
            >
                {loading ? "Organizing your tabs…" : "Organize Tabs"}
            </button>

            {/* Loading Skeleton */}
            {loading && (
                <div className="group">
                    <div className="skeleton" />
                    <div className="skeleton" />
                    <div className="skeleton" />
                </div>
            )}

            {/* Export Controls */}
            {groups && (
                <div className="controls">
                    <button className="control-btn secondary" onClick={() => setGroups(null)}>
                        ← Back
                    </button>
                    <button className="control-btn" onClick={() => exportSession("markdown")}>
                        Export MD
                    </button>
                    <button className="control-btn" onClick={() => exportSession("text")}>
                        Export Txt
                    </button>
                </div>
            )}

            {/* Render Groups */}
            {groups && groups.map((group, gi) => (
                <div key={gi} className="group-wrapper">
                    <div className="group-title">
                        <span className="group-dot" />
                        <div className="group-name accent-bar">
                            {group.name
                                .split(/\d+\.\s*/)
                                .filter(Boolean)
                                .map((line, i) => (
                                    <div key={i}>
                                        {i + 1}. {line}
                                    </div>
                                ))}
                        </div>
                    </div>

                    <TabGroup
                        group={group}
                        pinnedTabIds={pinnedTabIds}
                        onTogglePin={togglePin}
                    />
                </div>
            ))}

            {/* Recent Sessions */}
            {!groups && !loading && recentSessions.length > 0 && (
                <div className="recent-sessions">
                    <h3>Recent Sessions</h3>
                    {recentSessions.map((session, i) => {
                        const groups = Array.isArray(session.groups) ? session.groups : [];
                        return (
                            <div
                                key={i}
                                className="recent-session-item"
                                onClick={() => setGroups(groups)}
                            >
                                <span className="session-time">
                                    {new Date((session.created || 0) * 1000).toLocaleString()}
                                </span>
                                <span className="session-count">
                                    {groups.length} Groups
                                </span>
                            </div>
                        );
                    })}
                </div>
            )}

        </div>
    );
}
