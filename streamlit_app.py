import os
import streamlit as st
import requests
import time
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Rex's Lib chat — AI Library Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_DEFAULT = os.environ.get("API_BASE", "http://127.0.0.1:8000/api")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "libraryChat2026")

# ============================================================================
# SESSION STATE
# ============================================================================
_defaults = {
    "view": "welcome",
    "messages": [],
    "api_base": API_DEFAULT,
    "authenticated": False,
    "role": "public",
    "username": None,
    "show_login": False,
    "theme": "dark",
    "processing": False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

is_dark = st.session_state["theme"] == "dark"

# ============================================================================
# DESIGN SYSTEM
# ============================================================================
if is_dark:
    css_vars = """
        --bg-primary: #08090d;
        --bg-secondary: #0f1117;
        --bg-tertiary: #151821;
        --bg-card: linear-gradient(145deg, #12141d 0%, #161a26 100%);
        --bg-card-solid: #12141d;
        --bg-card-hover: #1a1e2e;
        --bg-input: #12141d;
        --bg-glass: rgba(15, 17, 23, 0.85);
        --bg-bubble-user: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        --bg-bubble-bot: #151821;
        --border-primary: rgba(255,255,255,0.08);
        --border-secondary: rgba(255,255,255,0.04);
        --border-glow: rgba(99, 102, 241, 0.3);
        --border-focus: #6366f1;
        --text-primary: #eaedf3;
        --text-secondary: #8891a5;
        --text-tertiary: #5a6178;
        --text-inverse: #ffffff;
        --text-on-brand: #ffffff;
        --brand-primary: #6366f1;
        --brand-secondary: #8b5cf6;
        --brand-hover: #7c7fff;
        --brand-subtle: rgba(99, 102, 241, 0.12);
        --brand-text: #a5b4fc;
        --brand-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
        --brand-gradient-hover: linear-gradient(135deg, #7c7fff 0%, #9d7dfa 50%, #b9a0fc 100%);
        --accent-pink: #ec4899;
        --accent-cyan: #22d3ee;
        --accent-emerald: #10b981;
        --accent-amber: #f59e0b;
        --success-bg: rgba(16, 185, 129, 0.1);
        --success-border: rgba(16, 185, 129, 0.25);
        --success-text: #34d399;
        --warning-bg: rgba(245, 158, 11, 0.1);
        --warning-border: rgba(245, 158, 11, 0.25);
        --warning-text: #fbbf24;
        --error-bg: rgba(239, 68, 68, 0.1);
        --error-border: rgba(239, 68, 68, 0.25);
        --error-text: #f87171;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.4);
        --shadow-md: 0 4px 20px rgba(0,0,0,0.5);
        --shadow-lg: 0 12px 40px rgba(0,0,0,0.6);
        --shadow-glow: 0 0 30px rgba(99, 102, 241, 0.15);
        --shadow-glow-lg: 0 0 60px rgba(99, 102, 241, 0.2);
        --confidence-high-bg: rgba(99, 102, 241, 0.12);
        --confidence-high-text: #a5b4fc;
        --confidence-low-bg: rgba(245, 158, 11, 0.12);
        --confidence-low-text: #fbbf24;
        --sidebar-bg: #0a0c12;
        --sidebar-border: rgba(255,255,255,0.06);
        --sidebar-input-bg: #12141d;
        --gradient-mesh-1: radial-gradient(ellipse at 20% 50%, rgba(99, 102, 241, 0.08) 0%, transparent 50%);
        --gradient-mesh-2: radial-gradient(ellipse at 80% 20%, rgba(139, 92, 246, 0.06) 0%, transparent 50%);
        --gradient-mesh-3: radial-gradient(ellipse at 60% 80%, rgba(236, 72, 153, 0.04) 0%, transparent 50%);
    """
else:
    css_vars = """
        --bg-primary: #fafbff;
        --bg-secondary: #f1f3f9;
        --bg-tertiary: #e8ebf4;
        --bg-card: linear-gradient(145deg, #ffffff 0%, #f8f9fd 100%);
        --bg-card-solid: #ffffff;
        --bg-card-hover: #f5f6fb;
        --bg-input: #ffffff;
        --bg-glass: rgba(250, 251, 255, 0.9);
        --bg-bubble-user: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        --bg-bubble-bot: #ffffff;
        --border-primary: rgba(0,0,0,0.08);
        --border-secondary: rgba(0,0,0,0.04);
        --border-glow: rgba(99, 102, 241, 0.25);
        --border-focus: #6366f1;
        --text-primary: #1a1d2d;
        --text-secondary: #64698a;
        --text-tertiary: #9ca0b8;
        --text-inverse: #ffffff;
        --text-on-brand: #ffffff;
        --brand-primary: #6366f1;
        --brand-secondary: #8b5cf6;
        --brand-hover: #5558e6;
        --brand-subtle: rgba(99, 102, 241, 0.07);
        --brand-text: #6366f1;
        --brand-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
        --brand-gradient-hover: linear-gradient(135deg, #5558e6 0%, #7c4ff0 50%, #9675f5 100%);
        --accent-pink: #ec4899;
        --accent-cyan: #06b6d4;
        --accent-emerald: #10b981;
        --accent-amber: #f59e0b;
        --success-bg: #ecfdf5;
        --success-border: #a7f3d0;
        --success-text: #065f46;
        --warning-bg: #fffbeb;
        --warning-border: #fcd34d;
        --warning-text: #92400e;
        --error-bg: #fef2f2;
        --error-border: #fca5a5;
        --error-text: #991b1b;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
        --shadow-md: 0 4px 20px rgba(0,0,0,0.08);
        --shadow-lg: 0 12px 40px rgba(0,0,0,0.12);
        --shadow-glow: 0 0 30px rgba(99, 102, 241, 0.1);
        --shadow-glow-lg: 0 0 60px rgba(99, 102, 241, 0.12);
        --confidence-high-bg: rgba(99, 102, 241, 0.08);
        --confidence-high-text: #5558e6;
        --confidence-low-bg: #fffbeb;
        --confidence-low-text: #92400e;
        --sidebar-bg: #f1f3f9;
        --sidebar-border: rgba(0,0,0,0.08);
        --sidebar-input-bg: #ffffff;
        --gradient-mesh-1: radial-gradient(ellipse at 20% 50%, rgba(99, 102, 241, 0.05) 0%, transparent 50%);
        --gradient-mesh-2: radial-gradient(ellipse at 80% 20%, rgba(139, 92, 246, 0.04) 0%, transparent 50%);
        --gradient-mesh-3: radial-gradient(ellipse at 60% 80%, rgba(236, 72, 153, 0.03) 0%, transparent 50%);
    """

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {{ {css_vars} }}

    /* ── Reset ────────────────────────────────────────────── */
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > div {{
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    /* Mesh gradient background */
    [data-testid="stAppViewContainer"]::before {{
        content: '';
        position: fixed;
        inset: 0;
        background:
            var(--gradient-mesh-1),
            var(--gradient-mesh-2),
            var(--gradient-mesh-3);
        pointer-events: none;
        z-index: 0;
    }}

    [data-testid="stHeader"] {{
        background: var(--bg-glass) !important;
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border-bottom: 1px solid var(--border-secondary) !important;
    }}

    /* ── Layout ───────────────────────────────────────────── */
    [data-testid="stAppViewContainer"] > div > div {{
        max-width: 920px;
        margin: 0 auto;
        padding: 0 1.25rem;
        position: relative;
        z-index: 1;
    }}

    /* ── Typography ───────────────────────────────────────── */
    .stMarkdown, .stMarkdown p, .stMarkdown li,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }}
    .stMarkdown a {{
        color: var(--brand-text) !important;
        text-decoration: none;
        transition: opacity 0.2s;
    }}
    .stMarkdown a:hover {{ opacity: 0.8; }}

    /* ── Sidebar ──────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--sidebar-border) !important;
        width: 300px !important;
        backdrop-filter: blur(12px);
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
    [data-testid="stSidebar"] .stTextInput > div > div > input {{
        background: var(--sidebar-input-bg) !important;
        color: var(--text-primary) !important;
        border: 1.5px solid var(--border-primary) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
    }}
    [data-testid="stSidebar"] .stTextInput > div > div > input:focus {{
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px var(--brand-subtle), var(--shadow-glow) !important;
    }}
    [data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {{
        color: var(--text-tertiary) !important;
    }}

    /* Sidebar Buttons */
    [data-testid="stSidebar"] .stButton > button {{
        background: var(--brand-gradient) !important;
        color: var(--text-on-brand) !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        padding: 0.55rem 1rem !important;
        transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
        letter-spacing: 0.01em;
        box-shadow: var(--shadow-sm);
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: var(--brand-gradient-hover) !important;
        box-shadow: var(--shadow-md), var(--shadow-glow);
        transform: translateY(-1px);
    }}
    [data-testid="stSidebar"] .stButton > button:active {{
        transform: translateY(0) scale(0.98);
    }}
    [data-testid="stSidebar"] .stButton > button * {{
        color: var(--text-on-brand) !important;
        background: transparent !important;
    }}

    /* Sidebar Alerts */
    [data-testid="stSidebar"] .stSuccess {{
        background: var(--success-bg) !important;
        border: 1px solid var(--success-border) !important;
        border-radius: 10px !important;
    }}
    [data-testid="stSidebar"] .stSuccess p {{ color: var(--success-text) !important; }}
    [data-testid="stSidebar"] .stWarning {{
        background: var(--warning-bg) !important;
        border: 1px solid var(--warning-border) !important;
        border-radius: 10px !important;
    }}
    [data-testid="stSidebar"] .stWarning p {{ color: var(--warning-text) !important; }}
    [data-testid="stSidebar"] .stError {{
        background: var(--error-bg) !important;
        border: 1px solid var(--error-border) !important;
        border-radius: 10px !important;
    }}
    [data-testid="stSidebar"] .stError p {{ color: var(--error-text) !important; }}
    [data-testid="stSidebar"] .stInfo {{
        background: var(--brand-subtle) !important;
        border: 1px solid var(--border-glow) !important;
        border-radius: 10px !important;
    }}
    [data-testid="stSidebar"] .stInfo p {{ color: var(--brand-text) !important; }}

    /* ── Main Inputs ──────────────────────────────────────── */
    .stTextInput > div > div > input {{
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
        border: 1.5px solid var(--border-primary) !important;
        border-radius: 14px !important;
        padding: 14px 20px !important;
        font-size: 15px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
        height: 52px !important;
        box-shadow: var(--shadow-sm) !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 4px var(--brand-subtle), var(--shadow-glow) !important;
        outline: none !important;
    }}
    .stTextInput > div > div > input::placeholder {{
        color: var(--text-tertiary) !important;
    }}
    .stTextInput label {{ color: var(--text-primary) !important; }}

    /* ── Main Buttons ─────────────────────────────────────── */
    .stButton > button {{
        background: var(--brand-gradient) !important;
        color: var(--text-on-brand) !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        font-family: 'Inter', sans-serif !important;
        padding: 14px 28px !important;
        cursor: pointer !important;
        transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
        letter-spacing: 0.01em;
        height: 52px !important;
        line-height: 1 !important;
        box-shadow: var(--shadow-sm) !important;
        position: relative;
        overflow: hidden;
    }}
    .stButton > button::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 50%);
        opacity: 0;
        transition: opacity 0.3s;
    }}
    .stButton > button:hover {{
        background: var(--brand-gradient-hover) !important;
        box-shadow: var(--shadow-md), var(--shadow-glow) !important;
        transform: translateY(-2px) !important;
    }}
    .stButton > button:hover::before {{
        opacity: 1;
    }}
    .stButton > button:active {{
        transform: translateY(0) scale(0.98) !important;
    }}
    .stButton > button * {{
        color: var(--text-on-brand) !important;
        background: transparent !important;
    }}

    /* Secondary button */
    .ghost-btn .stButton > button {{
        background: transparent !important;
        color: var(--text-secondary) !important;
        border: 1.5px solid var(--border-primary) !important;
        font-weight: 500 !important;
        font-size: 13.5px !important;
        height: 42px !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        padding: 10px 18px !important;
    }}
    .ghost-btn .stButton > button * {{
        color: var(--text-secondary) !important;
    }}
    .ghost-btn .stButton > button:hover {{
        background: var(--brand-subtle) !important;
        border-color: var(--border-glow) !important;
        color: var(--brand-text) !important;
        box-shadow: var(--shadow-glow) !important;
        transform: translateY(-1px) !important;
    }}
    .ghost-btn .stButton > button:hover * {{
        color: var(--brand-text) !important;
    }}

    /* ── Expanders ────────────────────────────────────────── */
    .stExpander {{
        background: var(--bg-card-solid) !important;
        border: 1px solid var(--border-primary) !important;
        border-radius: 14px !important;
        overflow: hidden;
        margin-bottom: 8px !important;
        transition: border-color 0.2s;
    }}
    .stExpander:hover {{
        border-color: var(--border-glow) !important;
    }}
    .stExpander summary,
    .stExpander [role="button"] {{
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        padding: 14px 18px !important;
    }}
    .stExpander [data-testid="stExpanderDetails"] {{
        border-top: 1px solid var(--border-secondary) !important;
        padding: 18px !important;
    }}

    /* ── Alerts ───────────────────────────────────────────── */
    .stSuccess {{ background: var(--success-bg) !important; border: 1px solid var(--success-border) !important; border-radius: 12px !important; }}
    .stSuccess p {{ color: var(--success-text) !important; }}
    .stWarning {{ background: var(--warning-bg) !important; border: 1px solid var(--warning-border) !important; border-radius: 12px !important; }}
    .stWarning p {{ color: var(--warning-text) !important; }}
    .stError {{ background: var(--error-bg) !important; border: 1px solid var(--error-border) !important; border-radius: 12px !important; }}
    .stError p {{ color: var(--error-text) !important; }}
    .stInfo {{ background: var(--brand-subtle) !important; border: 1px solid var(--border-glow) !important; border-radius: 12px !important; }}
    .stInfo p {{ color: var(--brand-text) !important; }}

    hr {{ border-color: var(--border-secondary) !important; }}

    /* ── File Uploader ────────────────────────────────────── */
    [data-testid="stFileUploader"] {{ color: var(--text-primary) !important; }}
    [data-testid="stFileUploader"] label {{ color: var(--text-primary) !important; }}
    [data-testid="stFileUploader"] section {{
        border: 2px dashed var(--border-primary) !important;
        border-radius: 14px !important;
        background: var(--bg-secondary) !important;
        transition: all 0.25s;
    }}
    [data-testid="stFileUploader"] section:hover {{
        border-color: var(--brand-primary) !important;
        background: var(--brand-subtle) !important;
    }}
    [data-testid="stFileUploader"] button {{
        background: var(--brand-gradient) !important;
        color: var(--text-on-brand) !important;
        border: none !important;
        border-radius: 10px !important;
    }}

    .stProgress > div > div {{
        background: var(--brand-gradient) !important;
        border-radius: 6px !important;
    }}

    /* ── Chat Bubbles ─────────────────────────────────────── */
    .chat-container {{
        display: flex;
        flex-direction: column;
        gap: 24px;
        padding: 28px 0;
    }}

    .msg-row {{
        display: flex;
        align-items: flex-end;
        gap: 12px;
        animation: msgSlideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .msg-row.user {{ flex-direction: row-reverse; }}

    @keyframes msgSlideIn {{
        from {{ opacity: 0; transform: translateY(16px) scale(0.97); }}
        to   {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}

    .avatar {{
        width: 38px;
        height: 38px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 15px;
        flex-shrink: 0;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}
    .avatar.user {{
        background: var(--brand-gradient);
        color: var(--text-on-brand);
        box-shadow: var(--shadow-sm), 0 0 16px rgba(99,102,241,0.2);
    }}
    .avatar.bot {{
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1.5px solid var(--border-primary);
    }}

    .bubble {{
        max-width: 72%;
        padding: 14px 20px;
        line-height: 1.7;
        font-size: 14.5px;
        word-wrap: break-word;
        white-space: pre-wrap;
        letter-spacing: 0.005em;
    }}
    .bubble.user {{
        background: var(--bg-bubble-user);
        color: var(--text-on-brand) !important;
        border-radius: 20px 6px 20px 20px;
        box-shadow: var(--shadow-md), 0 0 20px rgba(99,102,241,0.15);
    }}
    .bubble.bot {{
        background: var(--bg-bubble-bot);
        color: var(--text-primary) !important;
        border-radius: 6px 20px 20px 20px;
        border: 1px solid var(--border-primary);
        box-shadow: var(--shadow-sm);
    }}

    .msg-time {{
        font-size: 11px;
        color: var(--text-tertiary);
        margin-top: 6px;
        padding: 0 4px;
    }}
    .msg-row.user .msg-time {{ text-align: right; }}

    .confidence-badge {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 12px;
        padding: 5px 12px;
        border-radius: 8px;
        margin-top: 12px;
        font-weight: 600;
        letter-spacing: 0.02em;
        backdrop-filter: blur(8px);
    }}
    .confidence-high {{
        background: var(--confidence-high-bg);
        color: var(--confidence-high-text);
    }}
    .confidence-low {{
        background: var(--confidence-low-bg);
        color: var(--confidence-low-text);
    }}

    /* ── Welcome / Hero ───────────────────────────────────── */
    .hero {{
        text-align: center;
        padding: 56px 20px 36px;
        position: relative;
    }}

    .hero-logo {{
        width: 80px;
        height: 80px;
        border-radius: 24px;
        background: var(--brand-gradient);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 38px;
        margin-bottom: 24px;
        box-shadow: var(--shadow-lg), var(--shadow-glow-lg);
        position: relative;
        animation: logoFloat 6s ease-in-out infinite;
    }}
    @keyframes logoFloat {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-6px); }}
    }}
    @keyframes glow {{
        0%, 100% {{
            filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.5)) drop-shadow(0 0 40px rgba(139, 92, 246, 0.3));
        }}
        50% {{
            filter: drop-shadow(0 0 30px rgba(99, 102, 241, 0.8)) drop-shadow(0 0 60px rgba(139, 92, 246, 0.5));
        }}
    }}
    .hero-logo::after {{
        content: '';
        position: absolute;
        inset: -3px;
        border-radius: 27px;
        background: var(--brand-gradient);
        opacity: 0.3;
        filter: blur(12px);
        z-index: -1;
    }}

    .hero h1 {{
        font-size: 42px;
        font-weight: 800;
        color: var(--text-primary) !important;
        margin-bottom: 10px;
        letter-spacing: -0.035em;
        line-height: 1.15;
    }}
    .hero h1 .gradient-text {{
        background: var(--brand-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.5)) drop-shadow(0 0 40px rgba(139, 92, 246, 0.3));
        animation: glow 3s ease-in-out infinite;
    }}
    .hero .subtitle {{
        font-size: 17px;
        color: var(--text-secondary) !important;
        max-width: 460px;
        margin: 0 auto;
        line-height: 1.65;
        font-weight: 400;
    }}

    .section-label {{
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-tertiary) !important;
        margin-bottom: 20px;
        padding-left: 4px;
    }}

    /* ── Suggestion Cards ─────────────────────────────────── */
    .card-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 14px;
    }}
    .suggestion-card {{
        background: var(--bg-card);
        border: 1.5px solid var(--border-primary);
        border-radius: 18px;
        padding: 22px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
        text-decoration: none;
        display: flex;
        flex-direction: column;
        gap: 6px;
        position: relative;
        overflow: hidden;
    }}
    .suggestion-card::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, var(--brand-subtle) 0%, transparent 60%);
        opacity: 0;
        transition: opacity 0.3s;
    }}
    .suggestion-card:hover {{
        border-color: var(--border-glow);
        box-shadow: var(--shadow-md), var(--shadow-glow);
        transform: translateY(-4px);
    }}
    .suggestion-card:hover::before {{ opacity: 1; }}

    .card-icon {{
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        margin-bottom: 6px;
        position: relative;
    }}
    .card-icon.purple {{ background: rgba(99,102,241,0.12); }}
    .card-icon.pink   {{ background: rgba(236,72,153,0.12); }}
    .card-icon.cyan   {{ background: rgba(34,211,238,0.12); }}
    .card-icon.emerald {{ background: rgba(16,185,129,0.12); }}
    .card-icon.amber  {{ background: rgba(245,158,11,0.12); }}

    .card-title {{
        font-weight: 650;
        font-size: 15px;
        color: var(--text-primary);
        position: relative;
    }}
    .card-desc {{
        font-size: 13px;
        color: var(--text-secondary);
        line-height: 1.55;
        position: relative;
    }}

    /* ── Chat Header ──────────────────────────────────────── */
    .chat-header {{
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 20px 0 16px;
        border-bottom: 1px solid var(--border-secondary);
        margin-bottom: 4px;
    }}
    .chat-header-logo {{
        width: 46px;
        height: 46px;
        border-radius: 14px;
        background: var(--brand-gradient);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        color: white;
        flex-shrink: 0;
        box-shadow: var(--shadow-sm), 0 0 12px rgba(99,102,241,0.15);
    }}
    .chat-header-info h2 {{
        font-size: 18px;
        font-weight: 700;
        color: var(--text-primary) !important;
        margin: 0;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }}
    .chat-header-info .status {{
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: var(--text-secondary) !important;
        margin-top: 3px;
    }}
    .status-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent-emerald);
        display: inline-block;
        position: relative;
    }}
    .status-dot::after {{
        content: '';
        position: absolute;
        inset: -3px;
        border-radius: 50%;
        background: var(--accent-emerald);
        opacity: 0.3;
        animation: statusPulse 2s ease-in-out infinite;
    }}
    @keyframes statusPulse {{
        0%, 100% {{ transform: scale(1); opacity: 0.3; }}
        50% {{ transform: scale(1.5); opacity: 0; }}
    }}

    /* ── Empty State ──────────────────────────────────────── */
    .empty-state {{
        text-align: center;
        padding: 72px 20px;
    }}
    .empty-state-icon {{
        font-size: 56px;
        margin-bottom: 18px;
        opacity: 0.4;
        filter: grayscale(30%);
    }}
    .empty-state p {{
        font-size: 16px;
        color: var(--text-tertiary) !important;
        font-weight: 400;
    }}

    /* ── Typing Indicator ─────────────────────────────────── */
    .typing-indicator {{
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 8px 14px;
    }}
    .typing-dot {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--text-tertiary);
        animation: typingBounce 1.4s ease-in-out infinite;
    }}
    .typing-dot:nth-child(2) {{ animation-delay: 0.15s; }}
    .typing-dot:nth-child(3) {{ animation-delay: 0.3s; }}
    @keyframes typingBounce {{
        0%, 60%, 100% {{ transform: translateY(0); opacity: 0.4; }}
        30% {{ transform: translateY(-6px); opacity: 1; }}
    }}

    /* ── Powered-by Footer ────────────────────────────────── */
    .powered-by {{
        text-align: center;
        padding: 16px 0 8px;
        font-size: 12px;
        color: var(--text-tertiary) !important;
        letter-spacing: 0.02em;
    }}
    .powered-by span {{
        color: var(--brand-text) !important;
        font-weight: 600;
    }}

    /* ── Scrollbar ────────────────────────────────────────── */
    ::-webkit-scrollbar {{ width: 5px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border-primary);
        border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--text-tertiary); }}

    /* ── Responsive ───────────────────────────────────────── */
    @media (max-width: 768px) {{
        .hero h1 {{ font-size: 30px; }}
        .hero .subtitle {{ font-size: 15px; }}
        .bubble {{ max-width: 86%; font-size: 14px; padding: 12px 16px; }}
        .card-grid {{ grid-template-columns: 1fr; }}
        .hero-logo {{ width: 64px; height: 64px; font-size: 30px; border-radius: 18px; }}
        [data-testid="stAppViewContainer"] > div > div {{ padding: 0 0.75rem; }}
        .chat-header-logo {{ width: 40px; height: 40px; border-radius: 12px; font-size: 18px; }}
    }}

    /* ── Hide Streamlit UI chrome ─────────────────────────── */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    [data-testid="stSidebarNav"] {{ display: none; }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPERS
# ============================================================================
def add_message(role: str, text: str):
    st.session_state["messages"].append({
        "role": role,
        "text": text,
        "ts": time.time(),
    })


def fetch_menu() -> list[str]:
    try:
        r = requests.get(f"{st.session_state['api_base']}/menu", timeout=6)
        r.raise_for_status()
        return r.json().get("menu", [])
    except Exception:
        return ["Browse Catalog", "Loan Status", "Research Databases", "Study Spaces", "Library Services"]


def call_guided(option: str) -> dict:
    try:
        r = requests.post(f"{st.session_state['api_base']}/chat", json={"mode": "guided", "option": option}, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"answer": f"Service unavailable — {e}", "confidence": 0.0}


def call_ask(question: str) -> dict:
    try:
        r = requests.post(f"{st.session_state['api_base']}/chat", json={"mode": "ask", "question": question}, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"answer": f"Service unavailable — {e}", "confidence": 0.0}


CARD_META = {
    "Browse Catalog":     ("📖", "purple",  "Search our full book & media catalog"),
    "Loan Status":        ("📋", "pink",    "Check due dates, renewals & fines"),
    "Research Databases": ("🔍", "cyan",    "Access academic journals & databases"),
    "Study Spaces":       ("🏫", "emerald", "Find & reserve quiet study rooms"),
    "Library Services":   ("👥", "amber",   "Hours, contacts & support services"),
}


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fmt_time(ts: float) -> str:
    t = time.localtime(ts)
    h = t.tm_hour % 12 or 12
    ampm = "AM" if t.tm_hour < 12 else "PM"
    return f"{h}:{t.tm_min:02d} {ampm}"


# ============================================================================
# RENDER: MESSAGES
# ============================================================================
def render_messages():
    html = '<div class="chat-container">'
    for msg in st.session_state["messages"]:
        role = msg["role"]
        text = _esc(msg["text"])
        ts = _fmt_time(msg.get("ts", time.time()))
        conf_html = ""

        if role != "user" and "Confidence:" in text:
            try:
                parts = text.split("Confidence:")
                text = parts[0].strip()
                val = float(parts[1].strip().replace("%", ""))
                cls = "confidence-high" if val >= 50 else "confidence-low"
                ico = "✓" if val >= 50 else "⚠"
                conf_html = f'<div class="confidence-badge {cls}">{ico} {int(val)}%</div>'
            except Exception:
                pass

        if role == "user":
            html += f"""
            <div class="msg-row user">
                <div class="avatar user">U</div>
                <div>
                    <div class="bubble user">{text}</div>
                    <div class="msg-time">{ts}</div>
                </div>
            </div>"""
        else:
            html += f"""
            <div class="msg-row bot">
                <div class="avatar bot">📚</div>
                <div>
                    <div class="bubble bot">{text}{conf_html}</div>
                    <div class="msg-time">{ts}</div>
                </div>
            </div>"""

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ============================================================================
# SIDEBAR
# ============================================================================
def _sidebar_login():
    st.markdown("#### 🔐 Admin Sign In")
    u = st.text_input("Username", key="login_u", placeholder="Username")
    p = st.text_input("Password", type="password", key="login_p", placeholder="Password")
    if st.button("Sign In", use_container_width=True, key="btn_si"):
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            st.session_state.update(authenticated=True, role="admin", username=u, show_login=False)
            st.success("✅ Welcome back!")
            time.sleep(0.4)
            st.rerun()
        else:
            st.error("Invalid credentials")


def _sidebar_kb():
    with st.expander("📤 Knowledge Base", expanded=False):
        st.markdown("Upload documents to update AI knowledge.")
        files = st.file_uploader("Files", type=["txt", "pdf", "md"], accept_multiple_files=True)
        if files and st.button("Process & Index", use_container_width=True):
            os.makedirs("data", exist_ok=True)
            bar = st.progress(0)
            for i, f in enumerate(files):
                with open(f"data/{f.name}", "wb") as fp:
                    fp.write(f.getbuffer())
                bar.progress((i + 1) / len(files))
            st.success(f"✅ {len(files)} file(s) saved")
            with st.spinner("Reindexing…"):
                try:
                    r = requests.post(f"{st.session_state['api_base']}/reload", timeout=60)
                    if r.status_code == 200:
                        st.success("✅ Index updated")
                    else:
                        st.error(f"Reload failed with status {r.status_code}")
                except requests.exceptions.RequestException as e:
                    st.info("📚 Knowledge base files saved. Auto-reload skipped (backend may be restarting).")
                except Exception:
                    st.info("📚 Knowledge base files saved. Auto-reload skipped.")


def render_sidebar():
    with st.sidebar:
        # Header
        c1, c2 = st.columns([1, 1])
        with c1:
            name = st.session_state["username"] or "Guest"
            st.markdown(f"**👤 {name}**")
        with c2:
            lbl = "☀️ Light" if is_dark else "🌙 Dark"
            if st.button(lbl, use_container_width=True, key="thm"):
                st.session_state["theme"] = "light" if is_dark else "dark"
                st.rerun()

        st.divider()

        if st.session_state["authenticated"]:
            if st.button("🔓 Sign Out", use_container_width=True):
                st.session_state.update(authenticated=False, role="public", username=None, show_login=False)
                st.rerun()
        else:
            if st.button("🔒 Admin Login", use_container_width=True):
                st.session_state["show_login"] = not st.session_state["show_login"]
                st.rerun()

        if st.session_state["show_login"] and not st.session_state["authenticated"]:
            _sidebar_login()

        st.divider()

        if st.session_state["role"] == "admin":
            _sidebar_kb()

        with st.expander("⚙️ Settings", expanded=False):
            api = st.text_input("API Endpoint", value=st.session_state["api_base"])
            if api != st.session_state["api_base"]:
                st.session_state["api_base"] = api

        with st.expander("ℹ️ About", expanded=False):
            st.markdown("""
**Rex's Lib chat** — AI library assistant

**Tech Stack**
- RAG + FAISS vectors
- OpenAI GPT-4o-mini
- Streamlit
            """)

        # Sidebar footer
        st.markdown("---")
        st.markdown(
            '<p style="text-align:center;font-size:11px;color:var(--text-tertiary);">Rex\'s Lib chat v2.0</p>',
            unsafe_allow_html=True,
        )


# ============================================================================
# VIEW: WELCOME
# ============================================================================
def view_welcome():
    # Logo on top left
    logo_col, spacer = st.columns([0.15, 0.85])
    with logo_col:
        try:
            st.image("mewar logo.jpg", width=100)
        except Exception as e:
            st.error(f"Logo not found: {e}")
    
    st.markdown("""
    <div class="hero" style="padding-top: 20px;">
        <h1>Welcome to <span class="gradient-text">Rex's Lib chat</span></h1>
        <p class="subtitle">Your intelligent library companion. Ask questions, explore
        resources, and get instant help — powered by AI.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-label">Explore Topics</p>', unsafe_allow_html=True)

    opts = fetch_menu()
    cols = st.columns(min(len(opts), 3))

    for idx, opt in enumerate(opts):
        icon, color, desc = CARD_META.get(opt, ("💬", "purple", "Get help with this topic"))
        with cols[idx % len(cols)]:
            st.markdown(f"""
            <div class="suggestion-card" style="pointer-events:none;">
                <div class="card-icon {color}">{icon}</div>
                <div class="card-title">{opt}</div>
                <div class="card-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{opt}", key=f"opt_{idx}", use_container_width=True):
                add_message("user", opt)
                with st.spinner("Thinking…"):
                    res = call_guided(opt)
                add_message("bot", res.get("answer", "No response"))
                st.session_state["view"] = "chat"
                st.rerun()

    st.markdown("---")

    c1, c2, c3 = st.columns([1.2, 1, 1.8])
    with c1:
        if st.button("💬  Start a Conversation", use_container_width=True):
            st.session_state["view"] = "chat"
            st.rerun()

    st.markdown(
        '<div class="powered-by">Powered by <span>AI + RAG</span> technology</div>',
        unsafe_allow_html=True,
    )


# ============================================================================
# VIEW: CHAT
# ============================================================================
def view_chat():
    # Header
    st.markdown("""
    <div class="chat-header">
        <div class="chat-header-logo">📚</div>
        <div class="chat-header-info">
            <h2>Rex's Lib chat</h2>
            <div class="status">
                <span class="status-dot"></span>
                Online — ready to help
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Messages
    if st.session_state["messages"]:
        render_messages()
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">💬</div>
            <p>Type a message below to start chatting</p>
        </div>
        """, unsafe_allow_html=True)

    # Input
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    ci, cb = st.columns([6, 1])
    with ci:
        user_input = st.text_input(
            "Message",
            placeholder="Ask about books, hours, databases, borrowing…",
            key="chat_input",
            label_visibility="collapsed",
        )
    with cb:
        send = st.button("Send ➤", use_container_width=True, key="send_btn")

    if send and user_input:
        add_message("user", user_input)
        with st.spinner(""):
            res = call_ask(user_input)
        answer = res.get("answer", "No response")
        conf = res.get("confidence")
        if conf is not None and conf >= 0:
            answer += f"\n\nConfidence: {int(conf * 100)}%"
        add_message("bot", answer)
        st.rerun()

    # Footer
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("← Menu", key="back", use_container_width=True):
            st.session_state["view"] = "welcome"
            st.session_state["messages"] = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with f2:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("🗑 Clear", key="clr", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="powered-by">Powered by <span>AI + RAG</span> technology</div>',
        unsafe_allow_html=True,
    )


# ============================================================================
# MAIN
# ============================================================================
render_sidebar()

if st.session_state["view"] == "welcome":
    view_welcome()
elif st.session_state["view"] == "chat":
    view_chat()