import os
import streamlit as st
import requests
import hashlib
import time
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="LibraryChat — AI Library Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_DEFAULT = os.environ.get("API_BASE", "http://127.0.0.1:8000/api")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
_defaults = {
    "view": "welcome",
    "messages": [],
    "api_base": API_DEFAULT,
    "authenticated": False,
    "role": "public",
    "username": None,
    "show_login": False,
    "theme": "light",
    "processing": False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

is_dark = st.session_state["theme"] == "dark"

# ============================================================================
# DESIGN SYSTEM — COMPLETE CSS
# ============================================================================
if is_dark:
    css_vars = """
        --bg-primary: #0d1117;
        --bg-secondary: #161b22;
        --bg-tertiary: #1c2333;
        --bg-card: #1c2333;
        --bg-card-hover: #242d3d;
        --bg-input: #1c2333;
        --bg-bubble-user: #2563eb;
        --bg-bubble-bot: #1c2333;
        --border-primary: #30363d;
        --border-secondary: #21262d;
        --border-focus: #2563eb;
        --text-primary: #e6edf3;
        --text-secondary: #8b949e;
        --text-tertiary: #6e7681;
        --text-inverse: #ffffff;
        --text-on-brand: #ffffff;
        --brand-primary: #2563eb;
        --brand-hover: #3b82f6;
        --brand-subtle: rgba(37, 99, 235, 0.15);
        --brand-text: #58a6ff;
        --success-bg: rgba(46, 160, 67, 0.15);
        --success-border: rgba(46, 160, 67, 0.3);
        --success-text: #56d364;
        --warning-bg: rgba(210, 153, 34, 0.15);
        --warning-border: rgba(210, 153, 34, 0.3);
        --warning-text: #e3b341;
        --error-bg: rgba(248, 81, 73, 0.15);
        --error-border: rgba(248, 81, 73, 0.3);
        --error-text: #f85149;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
        --shadow-lg: 0 8px 24px rgba(0,0,0,0.5);
        --confidence-high-bg: rgba(37, 99, 235, 0.15);
        --confidence-high-text: #58a6ff;
        --confidence-low-bg: rgba(210, 153, 34, 0.15);
        --confidence-low-text: #e3b341;
        --sidebar-bg: #0d1117;
        --sidebar-border: #30363d;
        --sidebar-input-bg: #161b22;
    """
else:
    css_vars = """
        --bg-primary: #ffffff;
        --bg-secondary: #f6f8fa;
        --bg-tertiary: #f0f2f5;
        --bg-card: #ffffff;
        --bg-card-hover: #f6f8fa;
        --bg-input: #ffffff;
        --bg-bubble-user: #2563eb;
        --bg-bubble-bot: #f0f2f5;
        --border-primary: #d1d9e0;
        --border-secondary: #e8ecf0;
        --border-focus: #2563eb;
        --text-primary: #1f2937;
        --text-secondary: #656d76;
        --text-tertiary: #8b949e;
        --text-inverse: #ffffff;
        --text-on-brand: #ffffff;
        --brand-primary: #2563eb;
        --brand-hover: #1d4ed8;
        --brand-subtle: rgba(37, 99, 235, 0.08);
        --brand-text: #2563eb;
        --success-bg: #ecfdf5;
        --success-border: #a7f3d0;
        --success-text: #065f46;
        --warning-bg: #fffbeb;
        --warning-border: #fcd34d;
        --warning-text: #92400e;
        --error-bg: #fef2f2;
        --error-border: #fca5a5;
        --error-text: #991b1b;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
        --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
        --confidence-high-bg: rgba(37, 99, 235, 0.08);
        --confidence-high-text: #1d4ed8;
        --confidence-low-bg: #fffbeb;
        --confidence-low-text: #92400e;
        --sidebar-bg: #f6f8fa;
        --sidebar-border: #d1d9e0;
        --sidebar-input-bg: #ffffff;
    """

st.markdown(f"""
<style>
    :root {{ {css_vars} }}

    /* ── Reset & Base ─────────────────────────────────────── */
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > div {{
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter',
                     'Helvetica Neue', Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    [data-testid="stHeader"] {{
        background: var(--bg-primary) !important;
        border-bottom: 1px solid var(--border-secondary) !important;
    }}

    /* ── Layout Container ─────────────────────────────────── */
    [data-testid="stAppViewContainer"] > div > div {{
        max-width: 960px;
        margin: 0 auto;
        padding: 0 1rem;
    }}

    /* ── Typography ───────────────────────────────────────── */
    .stMarkdown, .stMarkdown p, .stMarkdown li,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
        color: var(--text-primary) !important;
    }}

    .stMarkdown a {{
        color: var(--brand-text) !important;
        text-decoration: none;
    }}
    .stMarkdown a:hover {{
        text-decoration: underline;
    }}

    /* ── Sidebar ──────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--sidebar-border) !important;
        width: 300px !important;
    }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li {{
        color: var(--text-primary) !important;
    }}
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown h4 {{
        color: var(--brand-text) !important;
        font-weight: 600 !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: var(--border-primary) !important;
    }}

    /* Sidebar Inputs */
    [data-testid="stSidebar"] .stTextInput input {{
        background: var(--sidebar-input-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-primary) !important;
        border-radius: 8px !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }}
    [data-testid="stSidebar"] .stTextInput input:focus {{
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px var(--brand-subtle) !important;
    }}
    [data-testid="stSidebar"] .stTextInput input::placeholder {{
        color: var(--text-tertiary) !important;
    }}

    /* Sidebar Buttons */
    [data-testid="stSidebar"] .stButton > button {{
        background: var(--brand-primary) !important;
        color: var(--text-on-brand) !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 0.5rem 1rem !important;
        transition: background 0.2s, transform 0.1s, box-shadow 0.2s;
        letter-spacing: 0.01em;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: var(--brand-hover) !important;
        box-shadow: var(--shadow-sm);
    }}
    [data-testid="stSidebar"] .stButton > button:active {{
        transform: scale(0.98);
    }}
    [data-testid="stSidebar"] .stButton > button * {{
        color: var(--text-on-brand) !important;
        background: transparent !important;
    }}

    /* Sidebar Alerts */
    [data-testid="stSidebar"] .stSuccess {{
        background: var(--success-bg) !important;
        border: 1px solid var(--success-border) !important;
        color: var(--success-text) !important;
        border-radius: 8px !important;
    }}
    [data-testid="stSidebar"] .stWarning {{
        background: var(--warning-bg) !important;
        border: 1px solid var(--warning-border) !important;
        color: var(--warning-text) !important;
        border-radius: 8px !important;
    }}
    [data-testid="stSidebar"] .stError {{
        background: var(--error-bg) !important;
        border: 1px solid var(--error-border) !important;
        color: var(--error-text) !important;
        border-radius: 8px !important;
    }}
    [data-testid="stSidebar"] .stInfo {{
        background: var(--brand-subtle) !important;
        border: 1px solid rgba(37, 99, 235, 0.25) !important;
        color: var(--brand-text) !important;
        border-radius: 8px !important;
    }}
    [data-testid="stSidebar"] .stInfo p {{
        color: var(--brand-text) !important;
    }}
    [data-testid="stSidebar"] .stSuccess p {{
        color: var(--success-text) !important;
    }}
    [data-testid="stSidebar"] .stWarning p {{
        color: var(--warning-text) !important;
    }}
    [data-testid="stSidebar"] .stError p {{
        color: var(--error-text) !important;
    }}

    /* ── Main Content Inputs ──────────────────────────────── */
    .stTextInput > div > div > input {{
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
        border: 1.5px solid var(--border-primary) !important;
        border-radius: 12px !important;
        padding: 12px 18px !important;
        font-size: 15px !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
        height: 48px !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px var(--brand-subtle) !important;
        outline: none !important;
    }}
    .stTextInput > div > div > input::placeholder {{
        color: var(--text-tertiary) !important;
    }}
    .stTextInput label {{
        color: var(--text-primary) !important;
    }}

    /* ── Main Content Buttons ─────────────────────────────── */
    .stButton > button {{
        background: var(--brand-primary) !important;
        color: var(--text-on-brand) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        padding: 12px 24px !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.01em;
        height: 48px !important;
        line-height: 1 !important;
    }}
    .stButton > button:hover {{
        background: var(--brand-hover) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }}
    .stButton > button:active {{
        transform: translateY(0) scale(0.98) !important;
    }}
    .stButton > button * {{
        color: var(--text-on-brand) !important;
        background: transparent !important;
    }}

    /* Secondary button style for footer actions */
    .secondary-btn .stButton > button {{
        background: transparent !important;
        color: var(--text-secondary) !important;
        border: 1.5px solid var(--border-primary) !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        height: 40px !important;
        border-radius: 10px !important;
    }}
    .secondary-btn .stButton > button * {{
        color: var(--text-secondary) !important;
    }}
    .secondary-btn .stButton > button:hover {{
        background: var(--bg-secondary) !important;
        border-color: var(--brand-primary) !important;
        color: var(--brand-text) !important;
        box-shadow: none !important;
        transform: none !important;
    }}
    .secondary-btn .stButton > button:hover * {{
        color: var(--brand-text) !important;
    }}

    /* ── Expanders ────────────────────────────────────────── */
    .stExpander {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border-primary) !important;
        border-radius: 12px !important;
        overflow: hidden;
        margin-bottom: 8px !important;
    }}
    .stExpander summary,
    .stExpander [role="button"] {{
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        padding: 12px 16px !important;
    }}
    .stExpander [data-testid="stExpanderDetails"] {{
        border-top: 1px solid var(--border-secondary) !important;
        padding: 16px !important;
    }}

    /* ── Alerts (main content) ────────────────────────────── */
    .stSuccess {{
        background: var(--success-bg) !important;
        border: 1px solid var(--success-border) !important;
        border-radius: 10px !important;
    }}
    .stSuccess p {{ color: var(--success-text) !important; }}
    .stWarning {{
        background: var(--warning-bg) !important;
        border: 1px solid var(--warning-border) !important;
        border-radius: 10px !important;
    }}
    .stWarning p {{ color: var(--warning-text) !important; }}
    .stError {{
        background: var(--error-bg) !important;
        border: 1px solid var(--error-border) !important;
        border-radius: 10px !important;
    }}
    .stError p {{ color: var(--error-text) !important; }}
    .stInfo {{
        background: var(--brand-subtle) !important;
        border: 1px solid rgba(37, 99, 235, 0.25) !important;
        border-radius: 10px !important;
    }}
    .stInfo p {{ color: var(--brand-text) !important; }}

    /* ── Divider ──────────────────────────────────────────── */
    hr {{
        border-color: var(--border-secondary) !important;
    }}

    /* ── File Uploader ────────────────────────────────────── */
    [data-testid="stFileUploader"] {{
        color: var(--text-primary) !important;
    }}
    [data-testid="stFileUploader"] label {{
        color: var(--text-primary) !important;
    }}
    [data-testid="stFileUploader"] section {{
        border: 2px dashed var(--border-primary) !important;
        border-radius: 12px !important;
        background: var(--bg-secondary) !important;
        transition: border-color 0.2s;
    }}
    [data-testid="stFileUploader"] section:hover {{
        border-color: var(--brand-primary) !important;
    }}
    [data-testid="stFileUploader"] button {{
        background: var(--brand-primary) !important;
        color: var(--text-on-brand) !important;
        border: none !important;
        border-radius: 8px !important;
    }}

    /* ── Progress Bar ─────────────────────────────────────── */
    .stProgress > div > div {{
        background: var(--brand-primary) !important;
        border-radius: 4px !important;
    }}

    /* ── Chat Bubbles ─────────────────────────────────────── */
    .chat-container {{
        display: flex;
        flex-direction: column;
        gap: 20px;
        padding: 24px 0;
    }}

    .msg-row {{
        display: flex;
        align-items: flex-start;
        gap: 12px;
        animation: msgFadeIn 0.3s ease-out;
    }}
    .msg-row.user {{
        flex-direction: row-reverse;
    }}

    @keyframes msgFadeIn {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}

    .avatar {{
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        flex-shrink: 0;
        font-weight: 600;
    }}
    .avatar.user {{
        background: var(--brand-primary);
        color: var(--text-on-brand);
    }}
    .avatar.bot {{
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border-primary);
    }}

    .bubble {{
        max-width: 72%;
        padding: 14px 18px;
        line-height: 1.65;
        font-size: 15px;
        word-wrap: break-word;
        white-space: pre-wrap;
    }}
    .bubble.user {{
        background: var(--bg-bubble-user);
        color: var(--text-on-brand) !important;
        border-radius: 18px 4px 18px 18px;
        box-shadow: var(--shadow-sm);
    }}
    .bubble.bot {{
        background: var(--bg-bubble-bot);
        color: var(--text-primary) !important;
        border-radius: 4px 18px 18px 18px;
        border: 1px solid var(--border-primary);
    }}

    .confidence-badge {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        padding: 4px 10px;
        border-radius: 6px;
        margin-top: 10px;
        font-weight: 600;
        letter-spacing: 0.02em;
    }}
    .confidence-high {{
        background: var(--confidence-high-bg);
        color: var(--confidence-high-text);
    }}
    .confidence-low {{
        background: var(--confidence-low-bg);
        color: var(--confidence-low-text);
    }}

    /* ── Welcome View ─────────────────────────────────────── */
    .hero {{
        text-align: center;
        padding: 48px 20px 32px;
    }}
    .hero-icon {{
        width: 64px;
        height: 64px;
        border-radius: 16px;
        background: var(--brand-subtle);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        margin-bottom: 20px;
        box-shadow: var(--shadow-sm);
    }}
    .hero h1 {{
        font-size: 36px;
        font-weight: 700;
        color: var(--text-primary) !important;
        margin-bottom: 8px;
        letter-spacing: -0.025em;
    }}
    .hero p {{
        font-size: 17px;
        color: var(--text-secondary) !important;
        max-width: 440px;
        margin: 0 auto;
        line-height: 1.6;
    }}

    .section-label {{
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-tertiary) !important;
        margin-bottom: 16px;
        padding-left: 2px;
    }}

    .suggestion-card {{
        background: var(--bg-card);
        border: 1.5px solid var(--border-primary);
        border-radius: 14px;
        padding: 20px;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        text-decoration: none;
        display: block;
        height: 100%;
    }}
    .suggestion-card:hover {{
        border-color: var(--brand-primary);
        background: var(--bg-card-hover);
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }}
    .suggestion-icon {{
        font-size: 28px;
        margin-bottom: 10px;
    }}
    .suggestion-title {{
        font-weight: 600;
        font-size: 15px;
        color: var(--text-primary);
        margin-bottom: 4px;
    }}
    .suggestion-desc {{
        font-size: 13px;
        color: var(--text-secondary);
        line-height: 1.5;
    }}

    /* ── Chat Header Bar ──────────────────────────────────── */
    .chat-header {{
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 16px 0;
        border-bottom: 1px solid var(--border-secondary);
        margin-bottom: 8px;
    }}
    .chat-header-icon {{
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: var(--brand-primary);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        color: white;
        flex-shrink: 0;
    }}
    .chat-header-text h2 {{
        font-size: 18px;
        font-weight: 700;
        color: var(--text-primary) !important;
        margin: 0;
        line-height: 1.2;
    }}
    .chat-header-text p {{
        font-size: 13px;
        color: var(--text-secondary) !important;
        margin: 2px 0 0;
    }}

    .status-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #22c55e;
        display: inline-block;
        margin-right: 4px;
        animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}

    /* ── Empty State ──────────────────────────────────────── */
    .empty-state {{
        text-align: center;
        padding: 60px 20px;
        color: var(--text-tertiary);
    }}
    .empty-state-icon {{
        font-size: 48px;
        margin-bottom: 16px;
        opacity: 0.5;
    }}
    .empty-state p {{
        font-size: 16px;
        color: var(--text-tertiary) !important;
    }}

    /* ── Scrollbar ────────────────────────────────────────── */
    ::-webkit-scrollbar {{
        width: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: transparent;
    }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border-primary);
        border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--text-tertiary);
    }}

    /* ── Responsive ───────────────────────────────────────── */
    @media (max-width: 768px) {{
        .hero h1 {{ font-size: 28px; }}
        .hero p {{ font-size: 15px; }}
        .bubble {{ max-width: 88%; font-size: 14px; }}
        .suggestion-card {{ padding: 16px; }}
        [data-testid="stAppViewContainer"] > div > div {{
            padding: 0 0.5rem;
        }}
    }}

    /* ── Spinner override ─────────────────────────────────── */
    .stSpinner > div {{
        border-top-color: var(--brand-primary) !important;
    }}

    /* ── Hide Streamlit branding ──────────────────────────── */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    [data-testid="stSidebarNav"] {{ display: none; }}
</style>
""", unsafe_allow_html=True)


# ============================================================================
# HELPERS
# ============================================================================
def add_message(role: str, text: str):
    st.session_state["messages"].append({"role": role, "text": text, "ts": time.time()})


def fetch_menu() -> list[str]:
    try:
        r = requests.get(f"{st.session_state['api_base']}/menu", timeout=6)
        r.raise_for_status()
        return r.json().get("menu", [])
    except Exception:
        return [
            "Browse Catalog",
            "Loan Status",
            "Research Databases",
            "Study Spaces",
            "Library Services",
        ]


def call_guided(option: str) -> dict:
    try:
        r = requests.post(
            f"{st.session_state['api_base']}/chat",
            json={"mode": "guided", "option": option},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"answer": f"Service unavailable — {e}", "confidence": 0.0}


def call_ask(question: str) -> dict:
    try:
        r = requests.post(
            f"{st.session_state['api_base']}/chat",
            json={"mode": "ask", "question": question},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"answer": f"Service unavailable — {e}", "confidence": 0.0}


ICON_MAP = {
    "Browse Catalog": ("📖", "Search our full book & media catalog"),
    "Loan Status": ("📋", "Check due dates, renewals & fines"),
    "Research Databases": ("🔍", "Access academic journals & databases"),
    "Study Spaces": ("🏫", "Find & reserve study rooms"),
    "Library Services": ("👥", "Hours, contacts & support services"),
}


def _escape(s: str) -> str:
    """Minimal HTML escaping."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ============================================================================
# RENDER: CHAT MESSAGES
# ============================================================================
def render_messages():
    html = '<div class="chat-container">'
    for msg in st.session_state["messages"]:
        role = msg["role"]
        text = _escape(msg["text"])
        conf_html = ""

        if role != "user" and "Confidence:" in text:
            try:
                parts = text.split("Confidence:")
                text = parts[0].strip()
                conf_val = float(parts[1].strip().replace("%", "").strip())
                cls = "confidence-high" if conf_val >= 50 else "confidence-low"
                icon = "✓" if conf_val >= 50 else "⚠"
                conf_html = (
                    f'<div class="confidence-badge {cls}">'
                    f"{icon} {int(conf_val)}% confident</div>"
                )
            except Exception:
                pass

        if role == "user":
            html += f"""
            <div class="msg-row user">
                <div class="avatar user">U</div>
                <div class="bubble user">{text}</div>
            </div>"""
        else:
            html += f"""
            <div class="msg-row bot">
                <div class="avatar bot">📚</div>
                <div class="bubble bot">{text}{conf_html}</div>
            </div>"""

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ============================================================================
# RENDER: SIDEBAR
# ============================================================================
def _sidebar_login():
    st.markdown("#### 🔐 Admin Login")
    username = st.text_input("Username", key="login_username", placeholder="Username")
    password = st.text_input(
        "Password", type="password", key="login_password", placeholder="Password"
    )
    if st.button("Sign In", use_container_width=True, key="btn_signin"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.update(
                authenticated=True, role="admin", username=username, show_login=False
            )
            st.success("✅ Signed in as admin")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Invalid credentials")


def _sidebar_admin_tools():
    with st.expander("📤 Knowledge Base", expanded=False):
        st.markdown("**Upload documents** to update the AI knowledge base.")
        uploaded = st.file_uploader(
            "Select files",
            type=["txt", "pdf", "md"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded and st.button("Process & Index", use_container_width=True):
            os.makedirs("data", exist_ok=True)
            bar = st.progress(0)
            for i, f in enumerate(uploaded):
                with open(f"data/{f.name}", "wb") as fp:
                    fp.write(f.getbuffer())
                bar.progress((i + 1) / len(uploaded))
            st.success(f"✅ {len(uploaded)} file(s) saved")
            with st.spinner("Reindexing…"):
                try:
                    r = requests.post(
                        f"{st.session_state['api_base']}/reload", timeout=60
                    )
                    if r.status_code == 200:
                        st.success("✅ Knowledge base updated")
                    else:
                        st.error("Reload failed — restart server")
                except Exception as e:
                    st.warning(f"Auto-reload failed: {e}")


def render_sidebar():
    with st.sidebar:
        # ── Top bar: user + theme toggle ──────────────────────
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.session_state["authenticated"]:
                st.markdown(f"**👤 {st.session_state['username']}**")
            else:
                st.markdown("**👤 Guest**")
        with c2:
            label = "☀️ Light" if is_dark else "🌙 Dark"
            if st.button(label, use_container_width=True, key="theme_toggle"):
                st.session_state["theme"] = "light" if is_dark else "dark"
                st.rerun()

        st.divider()

        # ── Auth button ──────────────────────────────────────
        if st.session_state["authenticated"]:
            if st.button("🔓 Sign Out", use_container_width=True):
                st.session_state.update(
                    authenticated=False, role="public", username=None, show_login=False
                )
                st.rerun()
        else:
            if st.button("🔒 Admin Login", use_container_width=True):
                st.session_state["show_login"] = not st.session_state["show_login"]
                st.rerun()

        if st.session_state["show_login"] and not st.session_state["authenticated"]:
            _sidebar_login()

        st.divider()

        # ── Admin tools ──────────────────────────────────────
        if st.session_state["role"] == "admin":
            _sidebar_admin_tools()

        # ── Settings ─────────────────────────────────────────
        with st.expander("⚙️ Settings", expanded=False):
            new_api = st.text_input(
                "API Endpoint",
                value=st.session_state["api_base"],
                help="Backend API base URL",
            )
            if new_api != st.session_state["api_base"]:
                st.session_state["api_base"] = new_api

        # ── About ────────────────────────────────────────────
        with st.expander("ℹ️ About", expanded=False):
            st.markdown(
                """
**LibraryChat** — AI-powered library assistant.

**Capabilities**
- 📚 Catalog search
- 📋 Loan management
- 🔍 Research databases
- 🏫 Study-space booking
- 📞 Service information

**Technology**
- RAG with FAISS
- OpenAI GPT-4o-mini
- Streamlit UI
            """
            )


# ============================================================================
# VIEW: WELCOME
# ============================================================================
def view_welcome():
    # Hero
    st.markdown(
        """
    <div class="hero">
        <div class="hero-icon">📚</div>
        <h1>LibraryChat</h1>
        <p>Your AI-powered library assistant. Ask about books, borrowing,
        study spaces, databases and more.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Section label
    st.markdown(
        '<p class="section-label">Quick Actions</p>', unsafe_allow_html=True
    )

    opts = fetch_menu()
    cols = st.columns(min(len(opts), 3))
    for idx, opt in enumerate(opts):
        icon, desc = ICON_MAP.get(opt, ("💬", "Get help with this topic"))
        with cols[idx % len(cols)]:
            # We render a styled card but use a real Streamlit button for interaction
            st.markdown(
                f"""
            <div class="suggestion-card" style="pointer-events:none;">
                <div class="suggestion-icon">{icon}</div>
                <div class="suggestion-title">{opt}</div>
                <div class="suggestion-desc">{desc}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            if st.button(f"Explore → {opt}", key=f"opt_{idx}", use_container_width=True):
                add_message("user", opt)
                with st.spinner("Thinking…"):
                    res = call_guided(opt)
                add_message("bot", res.get("answer", "No response"))
                st.session_state["view"] = "chat"
                st.rerun()

    st.markdown("---")

    col_left, col_right, _ = st.columns([1, 1, 2])
    with col_left:
        if st.button("💬 Ask a Question", use_container_width=True):
            st.session_state["view"] = "chat"
            st.rerun()


# ============================================================================
# VIEW: CHAT
# ============================================================================
def view_chat():
    # Header bar
    st.markdown(
        """
    <div class="chat-header">
        <div class="chat-header-icon">📚</div>
        <div class="chat-header-text">
            <h2>LibraryChat</h2>
            <p><span class="status-dot"></span>Online — ready to help</p>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Messages
    if st.session_state["messages"]:
        render_messages()
    else:
        st.markdown(
            """
        <div class="empty-state">
            <div class="empty-state-icon">💬</div>
            <p>Send a message to start the conversation</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # ── Input row ─────────────────────────────────────────
    st.markdown("")  # spacing
    c_input, c_btn = st.columns([6, 1])
    with c_input:
        user_input = st.text_input(
            "Message",
            placeholder="Ask about books, hours, databases, borrowing…",
            key="chat_input",
            label_visibility="collapsed",
        )
    with c_btn:
        send = st.button("Send ➤", use_container_width=True, key="send_btn")

    if send and user_input:
        add_message("user", user_input)
        with st.spinner("Thinking…"):
            res = call_ask(user_input)
        answer = res.get("answer", "No response")
        conf = res.get("confidence")
        if conf is not None and conf >= 0:
            answer += f"\n\nConfidence: {int(conf * 100)}%"
        add_message("bot", answer)
        st.rerun()

    # ── Footer actions ────────────────────────────────────
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("← Back to Menu", key="back_btn", use_container_width=True):
            st.session_state["view"] = "welcome"
            st.session_state["messages"] = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with f2:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("🗑 Clear Chat", key="clear_btn", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# MAIN ROUTER
# ============================================================================
render_sidebar()

if st.session_state["view"] == "welcome":
    view_welcome()
elif st.session_state["view"] == "chat":
    view_chat()