# dashboard.py
from flask import Flask, render_template_string

app = Flask(__name__)

TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Discord Live Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --bg: #020617;
            --card-bg: rgba(15, 23, 42, 0.85);
            --card-border: rgba(148, 163, 184, 0.4);
            --accent: #6366f1;
            --accent-soft: rgba(99, 102, 241, 0.2);
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --text-soft: #6b7280;
            --status-online: #22c55e;
            --status-idle: #facc15;
            --status-dnd: #ef4444;
            --status-offline: #4b5563;
            --blur: 20px;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
            min-height: 100vh;
            color: var(--text-main);
            background:
              radial-gradient(circle at top left, #0f172a 0, transparent 55%),
              radial-gradient(circle at bottom right, #020617 0, transparent 55%),
              linear-gradient(135deg, #020617 0, #000 100%);
            display: flex;
            flex-direction: column;
        }

        header {
            position: sticky;
            top: 0;
            z-index: 50;
            padding: 14px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(var(--blur));
            background: linear-gradient(to right, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.6));
            border-bottom: 1px solid rgba(148, 163, 184, 0.25);
        }

        header .left {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        header h1 {
            margin: 0;
            font-size: 20px;
            letter-spacing: 0.03em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .pill {
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.14);
            color: var(--text-soft);
        }

        header p {
            margin: 0;
            font-size: 13px;
            color: var(--text-muted);
        }

        .stats {
            display: flex;
            gap: 10px;
            align-items: center;
            font-size: 12px;
        }

        .stat-pill {
            padding: 6px 10px;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.3);
            background: radial-gradient(circle at top left, rgba(148, 163, 184, 0.15), transparent 60%);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .stat-pill strong { color: var(--text-main); }

        .content {
            display: grid;
            grid-template-columns: 260px 1fr;
            min-height: calc(100vh - 64px);
        }

        @media (max-width: 960px) {
            .content { grid-template-columns: 1fr; }
        }

        /* Sidebar */
        .sidebar {
            border-right: 1px solid rgba(148, 163, 184, 0.25);
            backdrop-filter: blur(var(--blur));
            background: linear-gradient(to bottom, rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.4));
            padding: 14px 12px;
            overflow-y: auto;
        }

        .sidebar-top {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 10px;
        }

        .sidebar h2 {
            margin: 0;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--text-soft);
        }

        .search-input {
            width: 100%;
            padding: 7px 9px;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.4);
            background: rgba(15, 23, 42, 0.9);
            color: var(--text-main);
            font-size: 12px;
            outline: none;
        }

        .search-input::placeholder {
            color: var(--text-soft);
        }

        .guild-list {
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-top: 8px;
        }

        .guild-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 7px 8px;
            border-radius: 999px;
            cursor: pointer;
            border: 1px solid transparent;
            transition: all 0.18s ease-out;
            text-decoration: none;
            color: inherit;
        }

        .guild-item.active {
            border-color: rgba(129, 140, 248, 0.9);
            background:
              radial-gradient(circle at top left, rgba(129, 140, 248, 0.4), transparent 60%),
              linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.4));
            transform: translateY(-1px) scale(1.01);
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.7);
        }

        .guild-item:hover:not(.active)) {
            border-color: rgba(148, 163, 184, 0.6);
            background: rgba(15, 23, 42, 0.7);
            transform: translateY(-1px);
        }

        .guild-avatar {
            width: 28px;
            height: 28px;
            border-radius: 12px;
            overflow: hidden;
            background: radial-gradient(circle at 20% 20%, #22c55e, #0f172a);
            border: 1px solid rgba(148, 163, 184, 0.5);
            flex-shrink: 0;
        }

        .guild-avatar img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .guild-meta {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .guild-name {
            font-size: 13px;
            font-weight: 500;
        }

        .guild-sub {
            font-size: 11px;
            color: var(--text-soft);
        }

        /* Main panel */
        .main {
            padding: 16px 20px 22px;
            overflow-y: auto;
        }

        .main-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            gap: 8px;
        }

        .main-header-left {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .current-guild-name {
            font-size: 16px;
            font-weight: 600;
        }

        .subtitle {
            font-size: 12px;
            color: var(--text-soft);
        }

        .main-header-right {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .refresh-indicator {
            font-size: 11px;
            color: var(--text-soft);
        }

        .sort-control {
            font-size: 11px;
            color: var(--text-soft);
        }

        .sort-select {
            margin-left: 4px;
            padding: 4px 8px;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.5);
            background: rgba(15, 23, 42, 0.95);
            color: var(--text-main);
            font-size: 11px;
            outline: none;
        }

        .members-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
            gap: 12px;
        }

        .members-grid.guild-switch {
            animation: guildSwitch 0.22s ease-out;
        }

        @keyframes guildSwitch {
            from {
                opacity: 0;
                transform: scale(0.97);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }

        .member-card {
            position: relative;
            padding: 11px;
            border-radius: 18px;
            border: 1px solid var(--card-border);
            background:
                radial-gradient(circle at top left, var(--accent-soft), transparent 60%),
                linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.8));
            backdrop-filter: blur(var(--blur));
            box-shadow:
                0 16px 30px rgba(15, 23, 42, 0.65),
                inset 0 0 0 1px rgba(15, 23, 42, 0.9);
            display: flex;
            flex-direction: column;
            gap: 8px;
            cursor: pointer;
            overflow: hidden;
            transform-origin: center;
            animation: cardIn 0.25s ease-out;
            transition: transform 0.16s ease-out, box-shadow 0.16s ease-out, border-color 0.16s ease-out;
        }

        @keyframes cardIn {
            from {
                opacity: 0;
                transform: translateY(6px) scale(0.98);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        .member-card:hover {
            transform: translateY(-2px) scale(1.01);
            box-shadow:
                0 24px 45px rgba(15, 23, 42, 0.85),
                0 0 0 1px rgba(129, 140, 248, 0.6);
            border-color: rgba(129, 140, 248, 0.7);
        }

        .member-top {
            display: flex;
            gap: 10px;
        }

        .avatar-wrap {
            position: relative;
            width: 44px;
            height: 44px;
            border-radius: 16px;
            overflow: hidden;
            background: radial-gradient(circle at 20% 20%, #4ade80, #020617);
            border: 1px solid rgba(148, 163, 184, 0.6);
            flex-shrink: 0;
        }

        .avatar-wrap img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .status-dot {
            position: absolute;
            right: -2px;
            bottom: -2px;
            width: 14px;
            height: 14px;
            border-radius: 999px;
            border: 3px solid #020617;
        }

        .status-online { background: var(--status-online); }
        .status-idle { background: var(--status-idle); }
        .status-dnd { background: var(--status-dnd); }
        .status-offline { background: var(--status-offline); }

        .member-main-info {
            display: flex;
            flex-direction: column;
            gap: 3px;
            min-width: 0;
        }

        .member-name {
            font-size: 14px;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .member-handle {
            font-size: 11px;
            color: var(--text-soft);
        }

        .member-roles {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 4px;
        }

        .role-pill {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 999px;
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(148, 163, 184, 0.5);
            color: var(--text-soft);
        }

        .member-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            color: var(--text-soft);
        }

        .badges-line {
            display: inline-flex;
            flex-wrap: wrap;
            gap: 4px;
        }

        .badge-chip {
            padding: 2px 6px;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.5);
            background: rgba(15, 23, 42, 0.9);
            font-size: 10px;
        }

        .activity {
            font-size: 11px;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .modal-activity-item {
            display: flex;
            gap: 10px;
            padding: 8px;
            border-radius: 8px;
            background: rgba(0,0,0,0.2);
            margin-bottom: 8px;
        }
        .modal-activity-item:last-child {
            margin-bottom: 0;
        }
        .modal-activity-assets {
            flex-shrink: 0;
        }
        .modal-activity-large-img {
            width: 60px;
            height: 60px;
            border-radius: 6px;
        }
        .modal-activity-info {
            display: flex;
            flex-direction: column;
            gap: 2px;
            font-size: 12px;
            min-width: 0; /* For ellipsis */
        }
        .modal-activity-name {
            font-weight: 600;
            color: var(--text-main);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .modal-activity-details, .modal-activity-state {
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .no-data {
            margin-top: 20px;
            font-size: 13px;
            color: var(--text-soft);
        }

        /* Modal */
        .modal-backdrop {
            position: fixed;
            inset: 0;
            background: radial-gradient(circle at top left, rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.96));
            backdrop-filter: blur(26px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 100;
            animation: backdropFadeIn 0.22s ease-out forwards;
        }

        @keyframes backdropFadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .modal-backdrop.open {
            display: flex;
        }

        .modal {
            width: min(420px, 92vw);
            border-radius: 22px;
            overflow: hidden;
            border: 1px solid rgba(129, 140, 248, 0.6);
            background:
                radial-gradient(circle at top left, rgba(129, 140, 248, 0.45), transparent 65%),
                linear-gradient(145deg, rgba(15, 23, 42, 0.98), rgba(15, 23, 42, 0.9));
            box-shadow:
                0 30px 65px rgba(15, 23, 42, 0.95),
                0 0 0 1px rgba(15, 23, 42, 0.9);
            transform-origin: center;
            animation: modalIn 0.25s cubic-bezier(0.19, 1, 0.22, 1);
        }

        @keyframes modalIn {
            from {
                opacity: 0;
                transform: translateY(12px) scale(0.96);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        .modal-banner {
            height: 110px;
            background: radial-gradient(circle at 20% 0%, rgba(129, 140, 248, 0.9), rgba(15, 23, 42, 0.95));
            position: relative;
            overflow: hidden;
        }

        .modal-banner img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            opacity: 0.9;
        }

        .modal-avatar {
            position: absolute;
            bottom: -28px;
            left: 20px;
            width: 72px;
            height: 72px;
            border-radius: 24px;
            overflow: hidden;
            border: 3px solid rgba(15, 23, 42, 1);
            background: radial-gradient(circle at 20% 20%, #4ade80, #020617);
        }

        .modal-avatar img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .modal-body {
            padding: 40px 20px 16px;
        }

        .modal-header-line {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 10px;
        }

        .modal-names {
            display: flex;
            flex-direction: column;
            gap: 3px;
        }

        .modal-display-name {
            font-size: 18px;
            font-weight: 600;
        }

        .modal-handle {
            font-size: 12px;
            color: var(--text-soft);
        }

        .modal-status-chip {
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.45);
            background: rgba(15, 23, 42, 0.9);
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }

        .status-dot-small {
            width: 8px;
            height: 8px;
            border-radius: 999px;
        }

        .modal-section {
            margin-top: 10px;
            font-size: 12px;
        }

        .modal-section-title {
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-size: 11px;
            color: var(--text-soft);
            margin-bottom: 4px;
        }

        .modal-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
        }

        .modal-chip {
            padding: 3px 7px;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.5);
            background: rgba(15, 23, 42, 0.9);
            font-size: 11px;
            color: var(--text-muted);
        }

        .activity-line {
            font-size: 12px;
            color: var(--text-muted);
        }

        .modal-footer {
            padding: 0 20px 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            color: var(--text-soft);
        }

        .close-btn {
            border: none;
            outline: none;
            border-radius: 999px;
            padding: 6px 12px;
            font-size: 12px;
            cursor: pointer;
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: #e5e7eb;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.7);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .close-btn span {
            font-size: 14px;
        }

        .footer-note {
            margin-top: 18px;
            font-size: 11px;
            color: var(--text-soft);
            text-align: right;
        }
    </style>
</head>
<body>
<header>
    <div class="left">
        <h1>
            Discord Live Dashboard
            <span class="pill">live · auto refresh</span>
        </h1>
        <p>Shows all members grouped by guild. Click any user for full profile.</p>
    </div>
    <div class="stats">
        <div class="stat-pill">
            <span>Guilds</span>
            <strong id="stat-guilds">0</strong>
        </div>
        <div class="stat-pill">
            <span>Members</span>
            <strong id="stat-members">0</strong>
        </div>
        <div class="stat-pill">
            <span>Last update</span>
            <strong id="stat-updated">—</strong>
        </div>
    </div>
</header>

<div class="content">
    <aside class="sidebar">
        <div class="sidebar-top">
            <h2>Guilds</h2>
            <input id="searchInput" class="search-input" placeholder="Search member by name...">
        </div>
        <div id="guildList" class="guild-list">
            <!-- Guild items injected -->
        </div>
    </aside>

    <main class="main">
        <div class="main-header">
            <div class="main-header-left">
                <div class="current-guild-name" id="currentGuildName">No guild selected</div>
                <div class="subtitle" id="currentGuildSubtitle">Waiting for data...</div>
            </div>
            <div class="main-header-right">
                <div class="refresh-indicator">
                    Refreshes every 7s · <span id="refreshStatus">idle</span>
                </div>
                <div class="sort-control">
                    Sort by
                    <select id="sortMode" class="sort-select">
                        <option value="status">Status (online → offline)</option>
                        <option value="name">Name (A → Z)</option>
                        <option value="role">Highest role</option>
                    </select>
                </div>
            </div>
        </div>

        <div id="membersGrid" class="members-grid">
            <!-- Member cards injected -->
        </div>

        <div id="noDataMsg" class="no-data" style="display:none;">
            No members to show. Is the bot online and in any guilds?
        </div>

        <div class="footer-note">
            Make sure <code>bot.py</code> is running. API: <code>http://127.0.0.1:5005/api/snapshot</code>
        </div>
    </main>
</div>

<!-- Modal -->
<div id="modalBackdrop" class="modal-backdrop" onclick="handleBackdropClick(event)">
    <div class="modal" onclick="event.stopPropagation();">
        <div class="modal-banner" id="modalBanner">
            <div class="modal-avatar" id="modalAvatar"></div>
        </div>
        <div class="modal-body">
            <div class="modal-header-line">
                <div class="modal-names">
                    <div class="modal-display-name" id="modalDisplayName">Display Name</div>
                    <div class="modal-handle" id="modalHandle">@user</div>
                </div>
                <div>
                    <div class="modal-status-chip" id="modalStatusChip">
                        <span class="status-dot-small" id="modalStatusDot"></span>
                        <span id="modalStatusText">offline</span>
                    </div>
                </div>
            </div>

            <div class="modal-section" id="modalBadgesSection" style="display:none;">
                <div class="modal-section-title">Badges</div>
                <div class="modal-chip-row" id="modalBadges"></div>
            </div>

            <div class="modal-section" id="modalRolesSection" style="display:none;">
                <div class="modal-section-title">Roles</div>
                <div class="modal-chip-row" id="modalRoles"></div>
            </div>

            <div class="modal-section" id="modalActivitySection" style="display:none;">
                <div class="modal-section-title">Activity</div>
                <div class="activity-line" id="modalActivity"></div>
            </div>

            <div class="modal-section">
                <div class="modal-section-title">Meta</div>
                <div class="activity-line" id="modalMeta"></div>
            </div>
        </div>
        <div class="modal-footer">
            <span id="modalFooterInfo">User ID: —</span>
            <button class="close-btn" onclick="closeModal()">
                <span>✕</span> Close
            </button>
        </div>
    </div>
</div>

<script>
const API_URL = "http://127.0.0.1:5005/api/snapshot";
const REFRESH_MS = 7000;

let snapshot = null;
let currentGuildId = null;
let prevGuildId = null;
let currentSearch = "";
let sortMode = "status";
let refreshTimer = null;

// Elements
const guildListEl = document.getElementById("guildList");
const membersGridEl = document.getElementById("membersGrid");
const noDataMsgEl = document.getElementById("noDataMsg");
const currentGuildNameEl = document.getElementById("currentGuildName");
const currentGuildSubtitleEl = document.getElementById("currentGuildSubtitle");
const statGuildsEl = document.getElementById("stat-guilds");
const statMembersEl = document.getElementById("stat-members");
const statUpdatedEl = document.getElementById("stat-updated");
const refreshStatusEl = document.getElementById("refreshStatus");
const searchInputEl = document.getElementById("searchInput");
const sortModeEl = document.getElementById("sortMode");

// Modal elements
const modalBackdropEl = document.getElementById("modalBackdrop");
const modalBannerEl = document.getElementById("modalBanner");
const modalAvatarEl = document.getElementById("modalAvatar");
const modalDisplayNameEl = document.getElementById("modalDisplayName");
const modalHandleEl = document.getElementById("modalHandle");
const modalStatusDotEl = document.getElementById("modalStatusDot");
const modalStatusTextEl = document.getElementById("modalStatusText");
const modalBadgesSectionEl = document.getElementById("modalBadgesSection");
const modalBadgesEl = document.getElementById("modalBadges");
const modalRolesSectionEl = document.getElementById("modalRolesSection");
const modalRolesEl = document.getElementById("modalRoles");
const modalActivitySectionEl = document.getElementById("modalActivitySection");
const modalActivityEl = document.getElementById("modalActivity");
const modalMetaEl = document.getElementById("modalMeta");
const modalFooterInfoEl = document.getElementById("modalFooterInfo");

function statusClass(status) {
    if (status === "online") return "status-online";
    if (status === "idle") return "status-idle";
    if (status === "dnd") return "status-dnd";
    return "status-offline";
}

function statusRank(status) {
    if (status === "online") return 0;
    if (status === "idle") return 1;
    if (status === "dnd") return 2;
    if (status === "offline") return 3;
    return 4;
}

function renderCardActivity(activity) {
    if (!activity) return '';
    let emoji = '💬';
    if (activity.type === 'playing') emoji = '🎮';
    if (activity.type === 'listening') emoji = '🎧';
    if (activity.type === 'streaming') emoji = '📺';

    if (activity.type === 'listening' && activity.title) {
        return `${emoji} ${activity.title} - ${activity.artists[0]}`;
    }
    
    let line = `${emoji} ${activity.name || ''}`;
    if (activity.details) line += `: ${activity.details}`;
    else if (activity.state) line += `: ${activity.state}`;

    return line;
}

function renderModalActivity(activity) {
    if (!activity) return '';

    // Use album art for spotify, or large asset for others
    let assetsHtml = '';
    const imageUrl = activity.album_cover_url || (activity.assets && activity.assets.large_image_url);
    if (imageUrl) {
        assetsHtml = `<div class="modal-activity-assets">
            <img src="${imageUrl}" class="modal-activity-large-img" alt="Activity asset">
        </div>`;
    }

    let infoHtml = '<div class="modal-activity-info">';
    
    if (activity.type === 'listening' && activity.title) {
        infoHtml += `<div class="modal-activity-name">Listening to ${activity.title}</div>`;
        if (activity.artists) infoHtml += `<div class="modal-activity-details">by ${activity.artists.join(', ')}</div>`;
        if (activity.album) infoHtml += `<div class="modal-activity-state">on ${activity.album}</div>`;
    } else {
        infoHtml += `<div class="modal-activity-name">${activity.name || 'Custom Activity'}</div>`;
        if (activity.details) {
            infoHtml += `<div class="modal-activity-details">${activity.details}</div>`;
        }
        if (activity.state) {
            infoHtml += `<div class="modal-activity-state">${activity.state}</div>`;
        }
    }
    
    infoHtml += '</div>';

    return `<div class="modal-activity-item">
        ${assetsHtml}
        ${infoHtml}
    </div>`;
}

function roleHexColor(role) {
    if (!role || role.color == null) return null;
    let hex = Number(role.color).toString(16).padStart(6, "0");
    return "#" + hex;
}

async function fetchSnapshot() {
    refreshStatusEl.textContent = "fetching...";
    try {
        const res = await fetch(API_URL);
        if (!res.ok) throw new Error("HTTP " + res.status);
        snapshot = await res.json();
        refreshStatusEl.textContent = "ok";
        renderSnapshot();
    } catch (e) {
        console.error("Failed to fetch snapshot:", e);
        refreshStatusEl.textContent = "error";
    }
}

function renderSnapshot() {
    if (!snapshot) return;

    const guilds = snapshot.guilds || [];
    statGuildsEl.textContent = guilds.length.toString();
    const totalMembers = guilds.reduce((sum, g) => sum + (g.members?.length || 0), 0);
    statMembersEl.textContent = totalMembers.toString();
    statUpdatedEl.textContent = snapshot.generated_at || "—";

    // Build guild list
    guildListEl.innerHTML = "";
    guilds.forEach(g => {
        const item = document.createElement("div");
        item.className = "guild-item" + (g.id === currentGuildId ? " active" : "");
        item.dataset.guildId = g.id;

        const ava = document.createElement("div");
        ava.className = "guild-avatar";
        if (g.icon_url) {
            const img = document.createElement("img");
            img.src = g.icon_url;
            img.alt = g.name;
            ava.appendChild(img);
        } else {
            const span = document.createElement("div");
            span.style.width = "100%";
            span.style.height = "100%";
            span.style.display = "flex";
            span.style.alignItems = "center";
            span.style.justifyContent = "center";
            span.style.fontSize = "14px";
            span.style.fontWeight = "700";
            span.textContent = g.name[0]?.toUpperCase() || "?";
            ava.appendChild(span);
        }

        const meta = document.createElement("div");
        meta.className = "guild-meta";

        const name = document.createElement("div");
        name.className = "guild-name";
        name.textContent = g.name;

        const sub = document.createElement("div");
        sub.className = "guild-sub";
        sub.textContent = `${g.member_count} members`;

        meta.appendChild(name);
        meta.appendChild(sub);

        item.appendChild(ava);
        item.appendChild(meta);

        item.addEventListener("click", () => {
            currentGuildId = g.id;
            renderSnapshot();
        });

        guildListEl.appendChild(item);
    });

    // Default guild selection
    if (!currentGuildId && guilds.length > 0) {
        currentGuildId = guilds[0].id;
    }

    const currentGuild = guilds.find(g => g.id === currentGuildId);
    if (!currentGuild) {
        currentGuildNameEl.textContent = "No guild selected";
        currentGuildSubtitleEl.textContent = "Select a guild from the left panel.";
        membersGridEl.innerHTML = "";
        noDataMsgEl.style.display = "block";
        return;
    }

    const guildChanged = currentGuildId !== prevGuildId;
    prevGuildId = currentGuildId;

    currentGuildNameEl.textContent = currentGuild.name;
    currentGuildSubtitleEl.textContent = `${currentGuild.members.length} member(s) · ID: ${currentGuild.id}`;

    const term = currentSearch.trim().toLowerCase();
    let members = (currentGuild.members || []).slice();

    if (term) {
        members = members.filter(m =>
            (m.display_name && m.display_name.toLowerCase().includes(term)) ||
            (m.name && m.name.toLowerCase().includes(term))
        );
    }

    // Sorting
    if (sortMode === "status") {
        members.sort((a, b) => {
            const ra = statusRank(a.status);
            const rb = statusRank(b.status);
            if (ra !== rb) return ra - rb;
            const na = (a.display_name || a.name || "").toLowerCase();
            const nb = (b.display_name || b.name || "").toLowerCase();
            return na.localeCompare(nb);
        });
    } else if (sortMode === "name") {
        members.sort((a, b) => {
            const na = (a.display_name || a.name || "").toLowerCase();
            const nb = (b.display_name || b.name || "").toLowerCase();
            return na.localeCompare(nb);
        });
    } else if (sortMode === "role") {
        function highestRolePos(m) {
            if (!m.roles || m.roles.length === 0) return -1;
            return Math.max(...m.roles.map(r => r.position || 0));
        }
        members.sort((a, b) => {
            const ra = highestRolePos(a);
            const rb = highestRolePos(b);
            if (ra !== rb) return rb - ra; // higher role first
            const na = (a.display_name || a.name || "").toLowerCase();
            const nb = (b.display_name || b.name || "").toLowerCase();
            return na.localeCompare(nb);
        });
    }

    membersGridEl.innerHTML = "";

    if (members.length === 0) {
        noDataMsgEl.style.display = "block";
        return;
    } else {
        noDataMsgEl.style.display = "none";
    }

    if (guildChanged) {
        membersGridEl.classList.remove("guild-switch");
        void membersGridEl.offsetWidth; // force reflow
        membersGridEl.classList.add("guild-switch");
        setTimeout(() => membersGridEl.classList.remove("guild-switch"), 250);
    }

    members.forEach(m => {
        const card = document.createElement("article");
        card.className = "member-card";

        const top = document.createElement("div");
        top.className = "member-top";

        const avatarWrap = document.createElement("div");
        avatarWrap.className = "avatar-wrap";
        if (m.avatar_url) {
            const img = document.createElement("img");
            img.src = m.avatar_url;
            img.alt = m.display_name || m.name;
            avatarWrap.appendChild(img);
        } else {
            const span = document.createElement("div");
            span.style.width = "100%";
            span.style.height = "100%";
            span.style.display = "flex";
            span.style.alignItems = "center";
            span.style.justifyContent = "center";
            span.style.fontSize = "18px";
            span.style.fontWeight = "700";
            span.textContent = (m.display_name || m.name || "?")[0].toUpperCase();
            avatarWrap.appendChild(span);
        }
        const sd = document.createElement("div");
        sd.className = "status-dot " + statusClass(m.status);
        avatarWrap.appendChild(sd);

        const mainInfo = document.createElement("div");
        mainInfo.className = "member-main-info";

        const name = document.createElement("div");
        name.className = "member-name";
        name.textContent = m.display_name || m.name;
        const handle = document.createElement("div");
        handle.className = "member-handle";
        handle.textContent = "@" + m.name + (m.discriminator && m.discriminator !== "0" ? "#" + m.discriminator : "");

        mainInfo.appendChild(name);
        mainInfo.appendChild(handle);

        if (m.roles && m.roles.length > 0) {
            const rolesWrap = document.createElement("div");
            rolesWrap.className = "member-roles";
            m.roles.slice(0, 3).forEach(r => {
                const pill = document.createElement("span");
                pill.className = "role-pill";
                pill.textContent = r.name;
                const color = roleHexColor(r);
                if (color) {
                    pill.style.borderColor = color;
                    pill.style.color = color;
                }
                rolesWrap.appendChild(pill);
            });
            if (m.roles.length > 3) {
                const more = document.createElement("span");
                more.className = "role-pill";
                more.textContent = "+" + (m.roles.length - 3);
                rolesWrap.appendChild(more);
            }
            mainInfo.appendChild(rolesWrap);
        }

        top.appendChild(avatarWrap);
        top.appendChild(mainInfo);

        const meta = document.createElement("div");
        meta.className = "member-meta";

        const badgeWrap = document.createElement("div");
        if (m.badges && m.badges.length > 0) {
            const line = document.createElement("div");
            line.className = "badges-line";
            m.badges.slice(0, 2).forEach(b => {
                const chip = document.createElement("span");
                chip.className = "badge-chip";
                chip.textContent = b.replace(/_/g, " ").toLowerCase();
                line.appendChild(chip);
            });
            if (m.badges.length > 2) {
                const more = document.createElement("span");
                more.className = "badge-chip";
                more.textContent = "+" + (m.badges.length - 2);
                line.appendChild(more);
            }
            badgeWrap.appendChild(line);
        }

        const joined = document.createElement("div");
        if (m.joined_at) {
            joined.textContent = "Joined " + m.joined_at.slice(0, 10);
        }

        meta.appendChild(badgeWrap);
        meta.appendChild(joined);

        const activity = document.createElement("div");
        activity.className = "activity";
        if (m.activities && m.activities.length > 0) {
            const first = m.activities[0];
            let text = renderCardActivity(first);
            if (m.activities.length > 1) {
                text += ` · +${m.activities.length - 1} more`;
            }
            activity.textContent = text;
        }

        card.appendChild(top);
        card.appendChild(meta);
        card.appendChild(activity);

        card.addEventListener("click", () => {
            openModal(currentGuild, m);
        });

        membersGridEl.appendChild(card);
    });
}

function openModal(guild, member) {
    modalBannerEl.innerHTML = "";
    if (member.banner_url) {
        const img = document.createElement("img");
        img.src = member.banner_url;
        modalBannerEl.appendChild(img);
    }

    modalAvatarEl.innerHTML = "";
    if (member.avatar_url) {
        const img = document.createElement("img");
        img.src = member.avatar_url;
        img.alt = member.display_name || member.name;
        modalAvatarEl.appendChild(img);
    } else {
        const span = document.createElement("div");
        span.style.width = "100%";
        span.style.height = "100%";
        span.style.display = "flex";
        span.style.alignItems = "center";
        span.style.justifyContent = "center";
        span.style.fontSize = "20px";
        span.style.fontWeight = "700";
        span.textContent = (member.display_name || member.name || "?")[0].toUpperCase();
        modalAvatarEl.appendChild(span);
    }

    modalDisplayNameEl.textContent = member.display_name || member.name;
    modalHandleEl.textContent = "@" + member.name + (member.discriminator && member.discriminator !== "0" ? "#" + member.discriminator : "");

    const statusCls = statusClass(member.status);
    modalStatusDotEl.className = "status-dot-small " + statusCls;
    modalStatusTextEl.textContent = member.status || "offline";

    modalBadgesEl.innerHTML = "";
    if (member.badges && member.badges.length > 0) {
        modalBadgesSectionEl.style.display = "block";
        member.badges.forEach(b => {
            const chip = document.createElement("span");
            chip.className = "modal-chip";
            chip.textContent = b.replace(/_/g, " ").toLowerCase();
            modalBadgesEl.appendChild(chip);
        });
    } else {
        modalBadgesSectionEl.style.display = "none";
    }

    modalRolesEl.innerHTML = "";
    if (member.roles && member.roles.length > 0) {
        modalRolesSectionEl.style.display = "block";
        member.roles.forEach(r => {
            const chip = document.createElement("span");
            chip.className = "modal-chip";
            chip.textContent = r.name;
            const color = roleHexColor(r);
            if (color) {
                chip.style.borderColor = color;
                chip.style.color = color;
            }
            modalRolesEl.appendChild(chip);
        });
    } else {
        modalRolesSectionEl.style.display = "none";
    }

    modalActivityEl.innerHTML = "";
    if (member.activities && member.activities.length > 0) {
        modalActivitySectionEl.style.display = "block";
        member.activities.forEach(act => {
            modalActivityEl.innerHTML += renderModalActivity(act);
        });
    } else {
        modalActivitySectionEl.style.display = "none";
    }

    const joined = member.joined_at ? member.joined_at.slice(0, 10) : "unknown";
    modalMetaEl.textContent = `Guild: ${guild.name} · Joined: ${joined}`;

    modalFooterInfoEl.textContent = `User ID: ${member.id} · Guild ID: ${guild.id}`;

    modalBackdropEl.classList.add("open");
}

function closeModal() {
    modalBackdropEl.classList.remove("open");
}

function handleBackdropClick(e) {
    closeModal();
}

// Search + sort listeners
searchInputEl.addEventListener("input", (e) => {
    currentSearch = e.target.value || "";
    renderSnapshot();
});

sortModeEl.addEventListener("change", (e) => {
    sortMode = e.target.value || "status";
    renderSnapshot();
});

// Start auto-refresh
fetchSnapshot();
refreshTimer = setInterval(fetchSnapshot, REFRESH_MS);
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(TEMPLATE)

if __name__ == "__main__":
    print("🌐 Dashboard running at http://127.0.0.1:5001")
    print("   Make sure bot.py is running (API on 5005)")
    app.run(host="127.0.0.1", port=5001, debug=False)
