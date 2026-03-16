import { useState } from "react";

export default function TabGroup({ group, pinnedTabIds, onTogglePin, onSmartRename }) {
    const [renamedTabs, setRenamedTabs] = useState({});

    if (!group || !Array.isArray(group.tabs)) return null;

    function handleRename(tab, index) {
        if (onSmartRename) {
            onSmartRename(tab.tabId);
            return;
        }
        const newTitle = prompt("Rename tab:", renamedTabs[index] ?? tab.title);
        if (newTitle && newTitle.trim()) {
            setRenamedTabs(prev => ({ ...prev, [index]: newTitle.trim() }));
        }
    }

    return (
        <div className="group">
            <h2 className="group-name">{group.name}</h2>
            {group.groupSummary && (
                <p className="group-summary">{group.groupSummary}</p>
            )}
            {group.tabs.map((tab, i) => {
                const isPinned = pinnedTabIds && pinnedTabIds.has(tab.tabId);
                const displayTitle = renamedTabs[i] ?? tab.title;
                return (
                    <div key={i} className="card">
                        <div className="tab-header">
                            <a href={tab.url} target="_blank" rel="noopener noreferrer" className="tab-title">
                                {displayTitle}
                            </a>
                            <div className="tab-actions">
                                {onTogglePin && (
                                    <button
                                        className={`pin-btn ${isPinned ? "pinned" : ""}`}
                                        onClick={() => onTogglePin(tab.tabId)}
                                        title={isPinned ? "Unpin tab" : "Pin tab"}
                                    >
                                        {isPinned ? "★" : "☆"}
                                    </button>
                                )}
                                <button
                                    className="smart-rename-btn"
                                    onClick={() => handleRename(tab, i)}
                                    title="Rename tab"
                                >
                                    ✎
                                </button>
                            </div>
                        </div>
                        <div className="tab-summary">
                            {typeof tab.summary === 'string' ? tab.summary : JSON.stringify(tab.summary)}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
