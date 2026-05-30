import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import urllib.parse
import hashlib
import json
import concurrent.futures
import io

# ─────────────────────────────────────────────
# 1. CONFIGURATION
# ─────────────────────────────────────────────
ADMIN_CREDENTIALS = {
    "9033004800": hashlib.sha256("9033004800".encode()).hexdigest(),
    "9023564826": hashlib.sha256("9023564826".encode()).hexdigest(),
}

st.set_page_config(
    page_title="OM Insurance Pro",
    layout="wide",
    page_icon="🏛️",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# 2. GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --navy:   #0a1628;
    --navy2:  #122040;
    --gold:   #c9a84c;
    --gold2:  #e8c97a;
    --silver: #8899aa;
    --light:  #f4f6f9;
    --white:  #ffffff;
    --green:  #16a34a;
    --red:    #dc2626;
    --amber:  #d97706;
    --blue:   #2563eb;
    --radius: 14px;
}

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.block-container { padding: 1.5rem 2rem 3rem; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--navy) 0%, var(--navy2) 100%);
    border-right: 1px solid rgba(201,168,76,0.25);
}
[data-testid="stSidebar"] * { color: #cdd6e4 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: var(--gold) !important; }

.header-banner {
    background: linear-gradient(135deg, var(--navy) 0%, #1a3060 60%, var(--navy2) 100%);
    border: 1px solid rgba(201,168,76,0.35);
    border-radius: var(--radius);
    padding: 28px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.header-banner::before {
    content:'';
    position:absolute; top:-40px; right:-40px;
    width:180px; height:180px;
    background: radial-gradient(circle, rgba(201,168,76,0.15) 0%, transparent 70%);
    border-radius:50%;
}
.header-banner h1 {
    font-family:'Playfair Display',serif;
    color:var(--gold) !important;
    font-size:2.1rem;
    margin:0 0 4px;
    letter-spacing:1px;
}
.header-banner p { color:#8899aa !important; margin:0; font-size:0.9rem; }

.metric-card {
    background:var(--white);
    border:1px solid #e2e8f0;
    border-radius:var(--radius);
    padding:20px 24px;
    position:relative;
    overflow:hidden;
    transition:box-shadow .2s;
}
.metric-card:hover { box-shadow:0 8px 28px rgba(10,22,40,0.10); }
.metric-card .label { font-size:0.78rem; color:var(--silver); text-transform:uppercase; letter-spacing:.7px; font-weight:600; }
.metric-card .value { font-family:'Playfair Display',serif; font-size:2rem; color:var(--navy); font-weight:700; line-height:1.1; margin-top:6px; }
.metric-card .sub   { font-size:0.78rem; color:var(--silver); margin-top:4px; }
.metric-card .accent { width:4px; height:100%; position:absolute; left:0; top:0; border-radius:var(--radius) 0 0 var(--radius); }
.accent-gold   { background:var(--gold); }
.accent-green  { background:var(--green); }
.accent-red    { background:var(--red); }
.accent-blue   { background:var(--blue); }

.clock-card {
    background: linear-gradient(135deg, #0f172a, #1e3a5f);
    border: 1px solid rgba(201,168,76,0.3);
    border-radius: var(--radius);
    padding: 20px;
    text-align: center;
    margin-bottom: 20px;
}
.clock-time { font-family:'Playfair Display',serif; font-size:2rem; color:var(--gold2); font-weight:700; }
.clock-date { color:#8899aa; font-size:0.85rem; margin-top:4px; }

[data-baseweb="tab-list"] { border-bottom:2px solid #e2e8f0; gap:4px; }
[data-baseweb="tab"] {
    font-family:'DM Sans',sans-serif; font-weight:600;
    color:var(--silver) !important;
    border-radius:8px 8px 0 0; padding:10px 20px;
}
[aria-selected="true"] { color:var(--navy) !important; border-bottom:2px solid var(--gold) !important; }

.wa-btn {
    background:linear-gradient(135deg,#25D366,#128C7E);
    color:white !important;
    padding:7px 16px;
    border-radius:20px;
    text-decoration:none;
    font-weight:600;
    font-size:0.82rem;
    display:inline-block;
    letter-spacing:.3px;
    transition:opacity .2s;
}
.wa-btn:hover { opacity:0.88; }

.policy-card {
    background: linear-gradient(135deg, var(--navy), #1a3060);
    border: 1px solid rgba(201,168,76,0.3);
    border-radius: var(--radius);
    padding: 24px 28px;
    color: white;
    margin: 20px auto;
    max-width: 520px;
}
.policy-card h2 { font-family:'Playfair Display',serif; color:var(--gold2); margin-bottom:16px; text-align:center; }
.policy-status-ok  { color:#4ade80; font-size:1.2rem; font-weight:700; }
.policy-status-exp { color:#f87171; font-size:1.2rem; font-weight:700; }
.policy-status-warn { color:#fbbf24; font-size:1.2rem; font-weight:700; }

.login-wrap { text-align:center; margin-bottom:12px; }
.login-wrap h3 { font-family:'Playfair Display',serif; color:var(--gold2) !important; font-size:1.1rem; }

.badge-renewed {
    background:#dcfce7; color:#15803d;
    font-size:0.72rem; font-weight:700;
    padding:2px 10px; border-radius:20px;
    display:inline-block; letter-spacing:.4px;
}
.badge-pending {
    background:#fef9c3; color:#92400e;
    font-size:0.72rem; font-weight:700;
    padding:2px 10px; border-radius:20px;
    display:inline-block; letter-spacing:.4px;
}
.badge-expired {
    background:#fee2e2; color:#991b1b;
    font-size:0.72rem; font-weight:700;
    padding:2px 10px; border-radius:20px;
    display:inline-block; letter-spacing:.4px;
}

.section-header {
    font-family:'Playfair Display',serif;
    color:var(--navy);
    font-size:1.25rem;
    font-weight:700;
    margin-bottom:16px;
    padding-bottom:8px;
    border-bottom:2px solid #f1f5f9;
}

.info-box {
    background:linear-gradient(135deg,#eff6ff,#dbeafe);
    border:1px solid #93c5fd;
    border-radius:var(--radius);
    padding:16px 20px;
    margin-bottom:16px;
    font-size:0.88rem;
    color:#1e40af;
}
.warn-box {
    background:linear-gradient(135deg,#fffbeb,#fef3c7);
    border:1px solid #fcd34d;
    border-radius:var(--radius);
    padding:16px 20px;
    margin-bottom:16px;
    font-size:0.88rem;
    color:#92400e;
}

.search-result-header {
    background: linear-gradient(135deg, #f8fafc, #f1f5f9);
    border: 1px solid #e2e8f0;
    border-radius: var(--radius);
    padding: 12px 18px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: var(--navy);
}

.print-btn {
    background: var(--navy);
    color: var(--gold) !important;
    padding: 8px 18px;
    border-radius: 20px;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.82rem;
    display: inline-block;
    border: 1px solid var(--gold);
    cursor: pointer;
    margin-top: 12px;
}

[data-testid="stDataEditor"] { border-radius:var(--radius); overflow:hidden; }
[data-testid="stSuccessMessage"] { border-radius:var(--radius); }

[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, var(--navy), #1a3060) !important;
    border:1px solid var(--gold) !important;
    color:var(--gold) !important;
    font-weight:600 !important;
    border-radius:10px !important;
}
[data-testid="baseButton-secondary"] {
    border-radius:10px !important;
    font-weight:600 !important;
}

.heatmap-cell {
    display:inline-block;
    width:22px; height:22px;
    border-radius:4px;
    margin:2px;
    text-align:center;
    font-size:0.65rem;
    line-height:22px;
    cursor:pointer;
}

@media print {
    .no-print { display: none !important; }
    .policy-card { border: 2px solid #c9a84c !important; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 3. HELPERS
# ─────────────────────────────────────────────

COLUMN_ALIASES = {
    'sr.no.'      : ['sr.no.', 'sr. no.', 'sr no', 'srno', 'sr', 'serial no', 'serial', 'sno', 's.no.'],
    'date'        : ['date', 'entry date', 'reg date'],
    'ins. st. dt.': ['ins. st. dt.', 'ins st dt', 'ins. st. date', 'ins st date', 'start date',
                     'ins start date', 'insurance start', 'ins. st. dt'],
    'ins. end dt.': ['ins. end dt.', 'ins end dt', 'ins. end date', 'ins end date', 'end date',
                     'expiry date', 'insurance end', 'ins. end dt', 'expiry'],
    'party name'  : ['party name', 'partyname', 'name', 'client name', 'customer name'],
    'm. no.'      : ['m. no.', 'm.no.', 'mobile', 'mobile no', 'mobile no.', 'phone', 'contact',
                     'mob no', 'mob. no.', 'm no'],
    'company'     : ['company', 'ins company', 'insurance company', 'insurer'],
    'type of ins.': ['type of ins.', 'type of ins', 'type', 'insurance type', 'ins type',
                     'type of insurance'],
    'premium'     : ['premium', 'prem', 'premium (₹)', 'premium amount'],
    'gst'         : ['gst', 'gst (₹)', 'tax'],
    'total'       : ['total', 'total (₹)', 'total amount', 'amount'],
    'policy.no.'  : ['policy.no.', 'policy no.', 'policy no', 'policy number', 'policy.no',
                     'policyno', 'policy #'],
    'renewed'     : ['renewed', 'renew', 'is renewed', 'renewal status'],
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    lowered = {c: c.lower().strip() for c in df.columns}
    for canonical, variants in COLUMN_ALIASES.items():
        for col, low in lowered.items():
            if low in variants and col not in rename_map:
                rename_map[col] = canonical
    df = df.rename(columns=rename_map)
    required = {
        'sr.no.': range(1, len(df) + 1),
        'date': '',
        'ins. st. dt.': pd.NaT,
        'ins. end dt.': pd.NaT,
        'party name': '',
        'm. no.': '',
        'company': '',
        'type of ins.': '',
        'premium': 0,
        'gst': 0,
        'total': 0,
        'policy.no.': '',
        'renewed': False,
    }
    for col, default in required.items():
        if col not in df.columns:
            df[col] = default
    return df


@st.cache_data
def get_period_options():
    return [datetime(y, m, 1).strftime('%B %Y')
            for y in range(2007, 2051) for m in range(1, 13)]


def clean_mobile(val):
    if isinstance(val, list):
        val = val[0] if val else ""
    if val is None:
        return ""
    s = str(val).strip()
    if s.lower() in ("nan", "none", ""):
        return ""
    if "." in s:
        s = s.split(".")[0]
    return s


def load_data(period_label: str):
    db_file = f"db_{period_label.replace(' ', '_')}.csv"

    if os.path.exists(db_file):
        df = pd.read_csv(db_file, dtype=str)
    else:
        st.info(f"📂 No records for **{period_label}**. Upload a CSV to initialise.")
        up = st.file_uploader("Choose CSV File", type="csv")
        if up:
            df = pd.read_csv(up, dtype=str)
            df = normalize_columns(df)
            df.to_csv(db_file, index=False)
            st.rerun()
        else:
            st.stop()

    df = normalize_columns(df)
    df['m. no.'] = df['m. no.'].apply(clean_mobile)
    df['ins. end dt.'] = pd.to_datetime(df['ins. end dt.'], dayfirst=True, errors='coerce')
    df['ins. st. dt.'] = pd.to_datetime(df['ins. st. dt.'], dayfirst=True, errors='coerce')
    df['renewed'] = df['renewed'].map(
        lambda x: True if str(x).strip().lower() in ('true', '1', 'yes') else False
    )
    for col in ['premium', 'gst', 'total']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df, db_file


def _load_csv_file(fpath: str):
    """Load and normalize a single CSV file — used by parallel loader."""
    try:
        tmp = pd.read_csv(fpath, dtype=str)
        tmp = normalize_columns(tmp)
        tmp['m. no.'] = tmp['m. no.'].apply(clean_mobile)
        tmp['ins. end dt.'] = pd.to_datetime(tmp['ins. end dt.'], dayfirst=True, errors='coerce')
        tmp['ins. st. dt.'] = pd.to_datetime(tmp['ins. st. dt.'], dayfirst=True, errors='coerce')
        tmp['renewed'] = tmp['renewed'].map(
            lambda x: True if str(x).strip().lower() in ('true', '1', 'yes') else False
        )
        for col in ['premium', 'gst', 'total']:
            tmp[col] = pd.to_numeric(tmp[col], errors='coerce').fillna(0)
        # tag source period
        period = fpath.replace("db_", "").replace(".csv", "").replace("_", " ")
        tmp['_period'] = period
        return tmp
    except Exception:
        return None


@st.cache_data(ttl=120)
def load_all_periods() -> pd.DataFrame:
    """Parallel-load ALL db_*.csv files and return combined DataFrame."""
    files = [f for f in os.listdir(".") if f.startswith("db_") and f.endswith(".csv")]
    if not files:
        return pd.DataFrame()
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(16, len(files))) as ex:
        results = list(ex.map(_load_csv_file, files))
    dfs = [r for r in results if r is not None and not r.empty]
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


def save_data(df: pd.DataFrame, path: str):
    df_save = df.copy()
    df_save['m. no.'] = df_save['m. no.'].apply(clean_mobile)
    df_save.to_csv(path, index=False)


def whatsapp_link(mobile: str, name: str, expiry) -> str:
    mobile = clean_mobile(mobile)
    if not mobile or len(mobile) < 10:
        return ""
    expiry_str = pd.Timestamp(expiry).strftime('%d %b %Y') if pd.notna(expiry) else "soon"
    msg = (
        f"🙏 Namaste {name},\n\n"
        f"Your insurance policy is expiring on *{expiry_str}*.\n"
        f"Please contact *OM Insurance & Investment* to renew.\n\n"
        f"📞 9033004800 | 9023564826\n"
        f"_Thank you for trusting OM Insurance._"
    )
    return f"https://wa.me/91{mobile}?text={urllib.parse.quote(msg)}"


def days_left_label(expiry, renewed):
    if renewed:
        return "✅ Renewed"
    if pd.isna(expiry):
        return "—"
    d = (pd.Timestamp(expiry).date() - datetime.now().date()).days
    if d < 0:
        return f"⛔ Expired {abs(d)}d ago"
    if d == 0:
        return "🔴 Expires TODAY"
    if d <= 7:
        return f"🔴 {d}d left"
    if d <= 30:
        return f"🟡 {d}d left"
    return f"🟢 {d}d left"


# ─────────────────────────────────────────────
# 4. SESSION STATE
# ─────────────────────────────────────────────
if "admin_auth"    not in st.session_state: st.session_state.admin_auth    = False
if "view_mode"     not in st.session_state: st.session_state.view_mode     = "admin"
if "search_history" not in st.session_state: st.session_state.search_history = []


# ─────────────────────────────────────────────
# 5. SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    now = datetime.now()
    st.markdown(f"""
        <div class="clock-card">
            <div class="clock-time">{now.strftime('%H:%M')}</div>
            <div class="clock-date">{now.strftime('%A, %d %B %Y')}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔀 Access Mode")
    mode = st.radio("", ["🏛️ Admin Panel", "🔍 Client Portal"],
                    index=0 if st.session_state.view_mode == "admin" else 1,
                    label_visibility="collapsed")
    st.session_state.view_mode = "admin" if "Admin" in mode else "client"

    st.divider()

    if st.session_state.view_mode == "admin":
        if not st.session_state.admin_auth:
            st.markdown('<div class="login-wrap"><h3>🔒 Admin Login</h3></div>', unsafe_allow_html=True)
            pwd = st.text_input("Mobile Number", type="password", placeholder="Enter admin mobile...")
            if st.button("🔓 Unlock Dashboard", use_container_width=True, type="primary"):
                h = hashlib.sha256(pwd.encode()).hexdigest()
                if any(h == v for v in ADMIN_CREDENTIALS.values()):
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
            st.stop()
        else:
            st.success("✅ Admin Authenticated")
            if st.button("🔒 Logout", use_container_width=True):
                st.session_state.admin_auth = False
                st.rerun()

            st.divider()
            st.markdown("### 📅 Working Period")
            periods = get_period_options()
            current_mo = now.strftime('%B %Y')
            choice = st.selectbox("Period", periods,
                                  index=periods.index(current_mo),
                                  label_visibility="collapsed")

            st.divider()
            st.markdown("### 📂 All Periods")
            all_files = sorted([
                f.replace("db_", "").replace(".csv", "").replace("_", " ")
                for f in os.listdir(".")
                if f.startswith("db_") and f.endswith(".csv")
            ])
            if all_files:
                st.caption(f"**{len(all_files)} period(s) loaded**")
                for p in all_files[-5:]:
                    st.caption(f"• {p}")
                if len(all_files) > 5:
                    st.caption(f"...and {len(all_files)-5} more")
            else:
                st.caption("No period data found.")


# ─────────────────────────────────────────────
# 6. CLIENT PORTAL — 24/7 anywhere access
# ─────────────────────────────────────────────
if st.session_state.view_mode == "client":
    st.markdown("""
        <div class="header-banner">
            <h1>🏛️ OM Insurance & Investment</h1>
            <p>Client Self-Service Portal — Check your policy expiry status instantly, 24 × 7</p>
        </div>
    """, unsafe_allow_html=True)

    # ── Contact strip
    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.markdown("📞 **9033004800**")
    col_c2.markdown("📞 **9023564826**")
    col_c3.markdown("🕐 Mon–Sat · 9AM–7PM")

    st.markdown("---")
    st.markdown('<div class="section-header">🔍 Policy Expiry Lookup</div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="info-box">
            🌐 This portal searches <strong>all available periods</strong> simultaneously.
            Enter your name as registered with OM Insurance to instantly view all your policies.
        </div>
    """, unsafe_allow_html=True)

    # ── Search form
    sc1, sc2, sc3 = st.columns([2, 1.5, 1])
    with sc1:
        client_name = st.text_input("Your Name", placeholder="Enter your name as registered...", key="cp_name")
    with sc2:
        policy_no   = st.text_input("Policy Number (optional)", placeholder="e.g. POL-2024-001", key="cp_pol")
    with sc3:
        mobile_srch = st.text_input("Mobile (optional)", placeholder="10-digit mobile", key="cp_mob")

    search_btn = st.button("🔎 Search All Policies", type="primary", use_container_width=False)

    # ── Recent searches
    if st.session_state.search_history:
        with st.expander("🕐 Recent Searches", expanded=False):
            for s in reversed(st.session_state.search_history[-5:]):
                if st.button(f"↩ {s}", key=f"hist_{s}"):
                    st.session_state["cp_name"] = s
                    st.rerun()

    if search_btn and (client_name or policy_no or mobile_srch):
        if client_name and client_name not in st.session_state.search_history:
            st.session_state.search_history.append(client_name)

        with st.spinner("🔍 Searching across all periods..."):
            all_df = load_all_periods()

        if all_df.empty:
            st.warning("⚠️ No policy database found. Please contact OM Insurance directly.")
            st.stop()

        mask = pd.Series([True] * len(all_df), index=all_df.index)
        if client_name:
            mask = mask & all_df['party name'].str.lower().str.contains(client_name.strip().lower(), na=False)
        if policy_no:
            mask = mask & all_df['policy.no.'].astype(str).str.contains(policy_no.strip(), na=False)
        if mobile_srch:
            m_clean = clean_mobile(mobile_srch)
            mask = mask & all_df['m. no.'].astype(str).str.contains(m_clean, na=False)

        found = all_df[mask].drop_duplicates(subset=['policy.no.', 'party name', 'ins. end dt.'])

        if found.empty:
            st.warning("❌ No policy found. Please contact OM Insurance: 📞 9033004800 / 9023564826")
        else:
            found_sorted = found.sort_values('ins. end dt.', ascending=False)
            st.success(f"✅ Found **{len(found_sorted)}** policy record(s)")

            # Summary strip
            total_pol   = len(found_sorted)
            renewed_pol = int(found_sorted['renewed'].sum())
            active_pol  = int(sum(
                1 for _, r in found_sorted.iterrows()
                if pd.notna(r['ins. end dt.']) and
                (r['ins. end dt.'].date() >= datetime.now().date()) and not r['renewed']
            ))
            expired_pol = total_pol - renewed_pol - active_pol

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Policies", total_pol)
            m2.metric("✅ Renewed", renewed_pol)
            m3.metric("🟢 Active", active_pol)
            m4.metric("❌ Expired/Due", expired_pol)

            st.markdown("---")

            for idx, (_, row) in enumerate(found_sorted.iterrows()):
                expiry   = row.get('ins. end dt.')
                renewed  = row.get('renewed', False)
                days_lft = (expiry.date() - datetime.now().date()).days if pd.notna(expiry) else None

                if renewed:
                    status_html   = '<span class="policy-status-ok">✅ RENEWED</span>'
                    status_badge  = '<span class="badge-renewed">✔ RENEWED</span>'
                elif days_lft is not None and days_lft < 0:
                    status_html   = f'<span class="policy-status-exp">❌ EXPIRED {abs(days_lft)} days ago</span>'
                    status_badge  = '<span class="badge-expired">✘ EXPIRED</span>'
                elif days_lft is not None and days_lft <= 30:
                    status_html   = f'<span class="policy-status-warn">⚠️ EXPIRING IN {days_lft} DAYS</span>'
                    status_badge  = '<span class="badge-pending">⚠ DUE SOON</span>'
                else:
                    status_html   = f'<span class="policy-status-ok">✅ ACTIVE ({days_lft} days left)</span>'
                    status_badge  = '<span class="badge-renewed">✔ ACTIVE</span>'

                period_tag = row.get('_period', '—')

                st.markdown(f"""
                    <div class="policy-card">
                        <h2>📋 Policy #{idx+1} &nbsp; {status_badge}</h2>
                        <table style="width:100%;text-align:left;color:#cdd6e4;font-size:0.88rem;">
                            <tr>
                                <td style="padding:6px 0;opacity:.6;width:40%;">Name</td>
                                <td style="font-weight:600;color:white;">{row.get('party name','—')}</td>
                            </tr>
                            <tr>
                                <td style="padding:6px 0;opacity:.6;">Policy No.</td>
                                <td style="color:var(--gold2);font-weight:600;">{row.get('policy.no.','—')}</td>
                            </tr>
                            <tr>
                                <td style="padding:6px 0;opacity:.6;">Insurance Company</td>
                                <td>{row.get('company','—')}</td>
                            </tr>
                            <tr>
                                <td style="padding:6px 0;opacity:.6;">Type</td>
                                <td>{row.get('type of ins.','—')}</td>
                            </tr>
                            <tr>
                                <td style="padding:6px 0;opacity:.6;">Start Date</td>
                                <td>{row['ins. st. dt.'].strftime('%d %b %Y') if pd.notna(row.get('ins. st. dt.')) else '—'}</td>
                            </tr>
                            <tr>
                                <td style="padding:6px 0;opacity:.6;">Expiry Date</td>
                                <td style="font-weight:600;">{expiry.strftime('%d %b %Y') if pd.notna(expiry) else '—'}</td>
                            </tr>
                            <tr>
                                <td style="padding:6px 0;opacity:.6;">Status</td>
                                <td>{status_html}</td>
                            </tr>
                            <tr>
                                <td style="padding:6px 0;opacity:.6;">Period</td>
                                <td style="opacity:.7;font-size:0.8rem;">{period_tag}</td>
                            </tr>
                        </table>
                        <div style="margin-top:18px;text-align:center;border-top:1px solid rgba(255,255,255,0.1);padding-top:14px;">
                            <span style="font-size:0.8rem;opacity:.6;">
                                For renewals & queries: 📞 9033004800 | 9023564826
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Print button for each card
                if st.button(f"🖨️ Print / Save Policy #{idx+1}", key=f"print_{idx}"):
                    st.info("Use your browser's Print function (Ctrl+P / Cmd+P) to save as PDF.")

            # ── Renewal reminder section
            needs_renewal = found_sorted[
                (found_sorted['renewed'] == False) &
                (found_sorted['ins. end dt.'].notna()) &
                (found_sorted['ins. end dt.'].apply(
                    lambda x: (x.date() - datetime.now().date()).days <= 30
                ))
            ]
            if not needs_renewal.empty:
                st.markdown("""
                    <div class="warn-box">
                        ⚠️ <strong>Action Required:</strong> You have policies expiring within 30 days.
                        Please contact OM Insurance immediately to avoid a lapse in coverage.
                        <br><br>📞 <strong>9033004800</strong> &nbsp;|&nbsp; 📞 <strong>9023564826</strong>
                    </div>
                """, unsafe_allow_html=True)

                for _, row in needs_renewal.iterrows():
                    mobile  = clean_mobile(row['m. no.'])
                    wa_link = whatsapp_link(mobile, row['party name'], row['ins. end dt.'])
                    if wa_link:
                        st.markdown(
                            f'<a href="{wa_link}" target="_blank" class="wa-btn">'
                            f'💬 WhatsApp Reminder for {row["policy.no."]}</a>',
                            unsafe_allow_html=True
                        )

    st.stop()


# ─────────────────────────────────────────────
# 7. ADMIN DASHBOARD
# ─────────────────────────────────────────────
df, active_path = load_data(choice)

st.markdown(f"""
    <div class="header-banner">
        <h1>🏛️ OM Insurance & Investment</h1>
        <p>Admin Control Panel &nbsp;|&nbsp; Period: <strong>{choice}</strong></p>
    </div>
""", unsafe_allow_html=True)

total_clients = len(df)
renewed_count = int(df['renewed'].sum())
pending_count = total_clients - renewed_count
total_premium = df['total'].sum()
expired_count = int(sum(
    1 for _, r in df.iterrows()
    if pd.notna(r['ins. end dt.']) and
    r['ins. end dt.'].date() < datetime.now().date() and not r['renewed']
))
expiring_30 = int(sum(
    1 for _, r in df.iterrows()
    if pd.notna(r['ins. end dt.']) and
    0 <= (r['ins. end dt.'].date() - datetime.now().date()).days <= 30
    and not r['renewed']
))

mc1, mc2, mc3, mc4, mc5 = st.columns(5)
with mc1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="accent accent-gold"></div>
            <div class="label">Total Clients</div>
            <div class="value">{total_clients}</div>
        </div>""", unsafe_allow_html=True)
with mc2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="accent accent-green"></div>
            <div class="label">Renewed</div>
            <div class="value">{renewed_count}</div>
            <div class="sub">{round(renewed_count/total_clients*100 if total_clients else 0)}% rate</div>
        </div>""", unsafe_allow_html=True)
with mc3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="accent accent-red"></div>
            <div class="label">Pending</div>
            <div class="value">{pending_count}</div>
        </div>""", unsafe_allow_html=True)
with mc4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="accent accent-red"></div>
            <div class="label">Expiring ≤30d</div>
            <div class="value">{expiring_30}</div>
            <div class="sub">action needed</div>
        </div>""", unsafe_allow_html=True)
with mc5:
    st.markdown(f"""
        <div class="metric-card">
            <div class="accent accent-blue"></div>
            <div class="label">Total Premium</div>
            <div class="value">₹{total_premium:,.0f}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

t1, t2, t3, t4, t5 = st.tabs([
    "📝 Smart Register",
    "💬 WhatsApp Alerts",
    "📊 Analysis",
    "🌐 Global Search",
    "⚙️ Settings"
])


# ══════════════════════════════════════════════
# TAB 1 — SMART REGISTER
# ══════════════════════════════════════════════
with t1:
    st.markdown('<div class="section-header">📋 Master Policy Register</div>', unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns([2, 1, 1])
    query        = sc1.text_input("🔍 Search by Client Name or Policy No.", placeholder="Start typing...", label_visibility="collapsed")
    show_pending = sc2.checkbox("Pending Only", value=False)
    show_expiring= sc3.checkbox("Expiring ≤30d", value=False)

    filtered = df.copy()
    if query:
        filtered = filtered[
            filtered['party name'].str.contains(query, case=False, na=False) |
            filtered['policy.no.'].astype(str).str.contains(query, case=False, na=False)
        ]
    if show_pending:
        filtered = filtered[filtered['renewed'] == False]
    if show_expiring:
        today = datetime.now().date()
        filtered = filtered[
            filtered['ins. end dt.'].apply(
                lambda x: pd.notna(x) and 0 <= (x.date() - today).days <= 30
            )
        ]

    filtered['m. no.'] = filtered['m. no.'].apply(clean_mobile)
    filtered['renewed'] = filtered['renewed'].astype(bool)

    st.caption(f"Showing **{len(filtered)}** of {total_clients} records")

    edited_df = st.data_editor(
        filtered,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "renewed":      st.column_config.CheckboxColumn("✅ Renewed", help="Tick when policy is renewed", default=False),
            "ins. end dt.": st.column_config.DateColumn("Expiry Date",  format="DD-MM-YYYY"),
            "ins. st. dt.": st.column_config.DateColumn("Start Date",   format="DD-MM-YYYY"),
            "premium":      st.column_config.NumberColumn("Premium (₹)", format="₹%d"),
            "gst":          st.column_config.NumberColumn("GST (₹)",     format="₹%d"),
            "total":        st.column_config.NumberColumn("Total (₹)",   format="₹%d"),
            "m. no.":       st.column_config.TextColumn("Mobile No."),
            "party name":   st.column_config.TextColumn("Client Name"),
        },
        hide_index=True,
    )

    sv1, sv2, sv3 = st.columns([1, 1, 3])
    if sv1.button("💾 Save Changes", type="primary", use_container_width=True):
        try:
            if query or show_pending or show_expiring:
                df.update(edited_df)
                save_data(df, active_path)
            else:
                save_data(edited_df, active_path)
            st.cache_data.clear()
            st.success("✅ Changes saved successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Save failed: {e}")

    if sv2.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # ── Bulk actions
    with st.expander("⚡ Bulk Actions", expanded=False):
        ba1, ba2 = st.columns(2)
        with ba1:
            st.markdown("**Mark all filtered as Renewed**")
            if st.button("✅ Bulk Mark Renewed", type="secondary"):
                df.loc[filtered.index, 'renewed'] = True
                save_data(df, active_path)
                st.cache_data.clear()
                st.success(f"Marked {len(filtered)} policies as renewed.")
                st.rerun()
        with ba2:
            st.markdown("**Export filtered to CSV**")
            csv_bytes = filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ Export Filtered",
                data=csv_bytes,
                file_name=f"OM_Filtered_{choice.replace(' ','_')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # ── Add new policy
    with st.expander("➕ Add New Policy", expanded=False):
        c1, c2, c3 = st.columns(3)
        n_name    = c1.text_input("Client Name *")
        n_mobile  = c2.text_input("Mobile Number")
        n_company = c3.text_input("Insurance Company")
        c4, c5, c6 = st.columns(3)
        n_type  = c4.text_input("Type of Insurance")
        n_start = c5.date_input("Start Date", value=datetime.now().date())
        n_end   = c6.date_input("Expiry Date", value=(datetime.now() + timedelta(days=365)).date())
        c7, c8, c9 = st.columns(3)
        n_prem  = c7.number_input("Premium (₹)", min_value=0.0, step=100.0)
        n_gst   = c8.number_input("GST (₹)",     min_value=0.0, step=10.0)
        n_total = c9.number_input("Total (₹)",   min_value=0.0, step=100.0, value=n_prem + n_gst)
        n_policy = st.text_input("Policy Number")

        if st.button("✚ Add Policy", type="primary"):
            if not n_name:
                st.error("Client name is required.")
            else:
                new_row = {
                    'sr.no.':       len(df) + 1,
                    'date':         datetime.now().strftime('%Y-%m-%d'),
                    'ins. st. dt.': str(n_start),
                    'ins. end dt.': str(n_end),
                    'party name':   n_name,
                    'm. no.':       clean_mobile(n_mobile),
                    'company':      n_company,
                    'type of ins.': n_type,
                    'premium':      n_prem,
                    'gst':          n_gst,
                    'total':        n_total,
                    'policy.no.':   n_policy,
                    'renewed':      False,
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df, active_path)
                st.cache_data.clear()
                st.success(f"✅ Policy added for {n_name}!")
                st.rerun()


# ══════════════════════════════════════════════
# TAB 2 — WHATSAPP ALERTS
# ══════════════════════════════════════════════
with t2:
    st.markdown('<div class="section-header">💬 WhatsApp Renewal Alerts</div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="info-box">
            📅 <strong>Weekly Schedule:</strong> Send alerts every Monday for policies expiring within 30 days.
            Adjust the range below and click WhatsApp to open chat directly.
        </div>
    """, unsafe_allow_html=True)

    aw1, aw2, aw3 = st.columns(3)
    days_range  = aw1.slider("Expiring within (days)", 1, 90, 30)
    show_all_wa = aw2.checkbox("Include already renewed", value=False)
    show_expired= aw3.checkbox("Include overdue/expired", value=True)

    tday  = datetime.now().date()
    limit = pd.Timestamp(tday + timedelta(days=days_range))

    alerts = df.copy()
    alerts['ins. end dt.'] = pd.to_datetime(alerts['ins. end dt.'], errors='coerce')
    alerts['m. no.']       = alerts['m. no.'].apply(clean_mobile)

    if show_expired:
        mask = alerts['ins. end dt.'] <= limit
    else:
        mask = (alerts['ins. end dt.'] <= limit) & (alerts['ins. end dt.'] >= pd.Timestamp(tday))

    if not show_all_wa:
        mask = mask & (alerts['renewed'] == False)

    to_send = alerts[mask].copy().sort_values('ins. end dt.')

    if not to_send.empty:
        # Summary
        has_mobile = to_send[to_send['m. no.'].str.len() >= 10]
        st.markdown(f"""
            <div class="search-result-header">
                📊 <strong>{len(to_send)} policies</strong> found &nbsp;|&nbsp;
                📱 <strong>{len(has_mobile)}</strong> have valid mobile numbers &nbsp;|&nbsp;
                ⚠️ <strong>{len(to_send[to_send['renewed']==False])}</strong> pending renewal
            </div>
        """, unsafe_allow_html=True)

        for i, row in to_send.iterrows():
            expiry    = row['ins. end dt.']
            days_left = (expiry.date() - tday).days if pd.notna(expiry) else None
            mobile    = clean_mobile(row['m. no.'])
            wa_link   = whatsapp_link(mobile, row['party name'], expiry)

            if days_left is not None and days_left < 0:
                urgency = f"⛔ {abs(days_left)}d OVERDUE"
            elif days_left is not None and days_left == 0:
                urgency = "🔴 TODAY"
            elif days_left is not None and days_left <= 7:
                urgency = f"🔴 {days_left}d left"
            else:
                urgency = f"🟡 {days_left}d left"

            renewed_badge = (
                '<span class="badge-renewed">✔ RENEWED</span>'
                if row['renewed']
                else '<span class="badge-pending">⏳ PENDING</span>'
            )

            col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 2])
            col_a.markdown(f"**{row['party name']}** &nbsp; {renewed_badge}", unsafe_allow_html=True)
            col_a.caption(f"{row.get('company','—')} · {row.get('type of ins.','—')}")
            col_b.write(expiry.strftime('%d %b %Y') if pd.notna(expiry) else "—")
            col_b.caption(f"Policy: {row.get('policy.no.','—')}")
            col_c.markdown(f"**{urgency}**")
            if wa_link:
                col_d.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn">💬 WhatsApp</a>', unsafe_allow_html=True)
            else:
                col_d.caption("❌ No number")
            st.divider()

        st.markdown("---")
        c_bulk1, c_bulk2 = st.columns(2)
        with c_bulk1:
            if st.button("📤 Open All WhatsApp Chats (max 10)", type="primary"):
                links = []
                for _, row in to_send.iterrows():
                    lnk = whatsapp_link(clean_mobile(row['m. no.']), row['party name'], row['ins. end dt.'])
                    if lnk:
                        links.append(lnk)
                if links:
                    js_links = "\n".join([f'window.open("{l}", "_blank");' for l in links[:10]])
                    st.components.v1.html(f"<script>{js_links}</script>", height=0)
                    st.success(f"Opening {min(len(links),10)} WhatsApp chats...")
                else:
                    st.warning("No valid mobile numbers found.")
        with c_bulk2:
            # Export alert list
            alert_csv = to_send[['party name', 'm. no.', 'policy.no.', 'ins. end dt.', 'company', 'type of ins.', 'renewed']].to_csv(index=False).encode()
            st.download_button("⬇️ Export Alert List", data=alert_csv,
                               file_name=f"Alerts_{choice.replace(' ','_')}.csv",
                               mime="text/csv", use_container_width=True)
    else:
        st.success("🎉 No pending renewals in this period!")


# ══════════════════════════════════════════════
# TAB 3 — ANALYSIS
# ══════════════════════════════════════════════
with t3:
    st.markdown('<div class="section-header">📊 Business Analytics</div>', unsafe_allow_html=True)

    if not df.empty:
        # ── Revenue summary
        r1, r2, r3 = st.columns(3)
        r1.metric("Total Premium Collected", f"₹{df['premium'].sum():,.0f}")
        r2.metric("Total GST", f"₹{df['gst'].sum():,.0f}")
        r3.metric("Total Revenue (incl. GST)", f"₹{df['total'].sum():,.0f}")

        st.markdown("---")

        a1, a2 = st.columns(2)

        with a1:
            st.markdown("**Policies by Company**")
            by_co = df.groupby('company').size().reset_index(name='Policies')
            by_co = by_co[by_co['company'].str.strip() != ''].sort_values('Policies', ascending=False)
            st.bar_chart(data=by_co, x='company', y='Policies', color='#c9a84c')

        with a2:
            st.markdown("**Renewal Status**")
            status_data = pd.DataFrame({
                'Status': ['Renewed', 'Pending'],
                'Count':  [renewed_count, pending_count]
            })
            st.bar_chart(data=status_data, x='Status', y='Count', color='#0a1628')

        a3, a4 = st.columns(2)
        with a3:
            st.markdown("**Insurance Type Distribution**")
            by_type = df.groupby('type of ins.').size().reset_index(name='Count')
            by_type = by_type[by_type['type of ins.'].str.strip() != ''].sort_values('Count', ascending=False)
            st.bar_chart(data=by_type, x='type of ins.', y='Count', color='#3b82f6')

        with a4:
            st.markdown("**Revenue by Company (₹)**")
            rev_co = df.groupby('company')['total'].sum().reset_index()
            rev_co = rev_co[rev_co['company'].str.strip() != ''].sort_values('total', ascending=False)
            st.bar_chart(data=rev_co, x='company', y='total', color='#16a34a')

        st.markdown("**Upcoming Expirations (next 60 days)**")
        upcoming = df[df['ins. end dt.'].notna()].copy()
        upcoming['ins. end dt.'] = pd.to_datetime(upcoming['ins. end dt.'])
        future = upcoming[
            (upcoming['ins. end dt.'] >= pd.Timestamp(datetime.now().date())) &
            (upcoming['ins. end dt.'] <= pd.Timestamp(datetime.now().date() + timedelta(days=60)))
        ]
        if not future.empty:
            future = future.copy()
            future['Week'] = future['ins. end dt.'].dt.strftime('W%V %b')
            weekly = future.groupby('Week').size().reset_index(name='Expiring')
            st.bar_chart(data=weekly, x='Week', y='Expiring', color='#dc2626')
        else:
            st.info("No expirations in next 60 days.")

        # ── Expiry heatmap by day of month
        st.markdown("**Expiry Day-of-Month Distribution**")
        if not df['ins. end dt.'].isna().all():
            dom = df['ins. end dt.'].dropna().dt.day.value_counts().sort_index()
            dom_df = pd.DataFrame({'Day': dom.index, 'Policies': dom.values})
            st.bar_chart(data=dom_df, x='Day', y='Policies', color='#7c3aed')

    else:
        st.info("No data available for analysis.")


# ══════════════════════════════════════════════
# TAB 4 — GLOBAL SEARCH (all periods)
# ══════════════════════════════════════════════
with t4:
    st.markdown('<div class="section-header">🌐 Global Search — All Periods</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="info-box">
            🔍 Search simultaneously across <strong>all loaded CSV periods</strong>.
            Find any client's complete insurance history instantly.
        </div>
    """, unsafe_allow_html=True)

    gs1, gs2 = st.columns([3, 1])
    g_query = gs1.text_input("Search client name, policy no., or mobile", placeholder="Start typing...", key="global_search")
    g_btn   = st.button("🔎 Search All Periods", type="primary")

    if g_btn and g_query:
        with st.spinner("Loading all periods in parallel..."):
            all_data = load_all_periods()

        if all_data.empty:
            st.warning("No period data found. Please upload CSVs first.")
        else:
            gm = (
                all_data['party name'].str.lower().str.contains(g_query.lower(), na=False) |
                all_data['policy.no.'].astype(str).str.contains(g_query, na=False) |
                all_data['m. no.'].astype(str).str.contains(clean_mobile(g_query), na=False)
            )
            g_results = all_data[gm].sort_values('ins. end dt.', ascending=False)

            if g_results.empty:
                st.warning("No results found across any period.")
            else:
                st.success(f"Found **{len(g_results)}** records across **{g_results['_period'].nunique()}** period(s)")

                display_cols = ['party name', 'policy.no.', 'company', 'type of ins.',
                                'ins. st. dt.', 'ins. end dt.', 'total', 'renewed', '_period']
                existing_cols = [c for c in display_cols if c in g_results.columns]
                st.dataframe(
                    g_results[existing_cols].rename(columns={'_period': 'Period'}),
                    use_container_width=True,
                    hide_index=True
                )

                g_csv = g_results[existing_cols].to_csv(index=False).encode()
                st.download_button("⬇️ Export Results", data=g_csv,
                                   file_name=f"GlobalSearch_{g_query[:20]}.csv",
                                   mime="text/csv")

    # ── Cross-period stats
    st.markdown("---")
    st.markdown("**Cross-Period Portfolio Overview**")
    if st.button("📊 Load Portfolio Stats"):
        with st.spinner("Aggregating all periods..."):
            port = load_all_periods()
        if not port.empty:
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Total Policies (all time)", len(port))
            p2.metric("Total Revenue (all time)", f"₹{port['total'].sum():,.0f}")
            p3.metric("Unique Clients", port['party name'].nunique())
            p4.metric("Periods Available", port['_period'].nunique())

            st.markdown("**Revenue by Period**")
            rev_period = port.groupby('_period')['total'].sum().reset_index().sort_values('_period')
            st.bar_chart(data=rev_period, x='_period', y='total', color='#c9a84c')
        else:
            st.info("No data found.")


# ══════════════════════════════════════════════
# TAB 5 — SETTINGS
# ══════════════════════════════════════════════
with t5:
    st.markdown('<div class="section-header">⚙️ Data Management</div>', unsafe_allow_html=True)

    s1, s2 = st.columns(2)

    with s1:
        st.markdown("**📤 Export Current Period**")
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Download CSV",
            data=csv_bytes,
            file_name=f"OM_Insurance_{choice.replace(' ','_')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("**📤 Export All Periods (combined)**")
        if st.button("📦 Build Combined Export"):
            with st.spinner("Combining all periods..."):
                all_exp = load_all_periods()
            if not all_exp.empty:
                combined_csv = all_exp.to_csv(index=False).encode()
                st.download_button(
                    "⬇️ Download All Periods",
                    data=combined_csv,
                    file_name="OM_Insurance_AllPeriods.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    with s2:
        st.markdown("**📥 Import / Replace Data**")
        up2 = st.file_uploader("Upload new CSV", type="csv", key="settings_upload")
        if up2 and st.button("🔄 Replace Database", type="primary"):
            new_df = pd.read_csv(up2, dtype=str)
            new_df = normalize_columns(new_df)
            new_df['m. no.'] = new_df['m. no.'].apply(clean_mobile)
            save_data(new_df, active_path)
            st.cache_data.clear()
            st.success("Database replaced!")
            st.rerun()

        st.markdown("**📥 Bulk Import (Multiple CSVs)**")
        multi_up = st.file_uploader("Upload multiple CSVs", type="csv",
                                    accept_multiple_files=True, key="bulk_upload")
        if multi_up and st.button("📤 Import All Uploaded Files", type="secondary"):
            imported = 0
            for f in multi_up:
                try:
                    tmp = pd.read_csv(f, dtype=str)
                    tmp = normalize_columns(tmp)
                    tmp['m. no.'] = tmp['m. no.'].apply(clean_mobile)
                    fname = f"db_{f.name.replace('.csv','').replace(' ','_')}.csv"
                    tmp.to_csv(fname, index=False)
                    imported += 1
                except Exception as ex:
                    st.warning(f"Could not import {f.name}: {ex}")
            if imported:
                st.cache_data.clear()
                st.success(f"✅ Imported {imported} file(s) successfully!")
                st.rerun()

    st.markdown("---")
    st.markdown("**🗑️ Danger Zone**")
    if st.checkbox("I understand this will DELETE all records for this period"):
        if st.button("🗑️ Clear This Period's Data", type="secondary"):
            if os.path.exists(active_path):
                os.remove(active_path)
                st.cache_data.clear()
                st.success("Period data deleted.")
                st.rerun()
