import streamlit as st
import pandas as pd
from src.data_processing.schema import map_and_validate_csv, STANDARD_COLUMNS

# Page config
st.set_page_config(page_title="Strategic Content Analyzer", layout="wide", initial_sidebar_state="expanded")

# Premium CSS styling
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background with gradient and neural network effect */
    .stApp {
        background: linear-gradient(135deg, #0B1220 0%, #111B2E 100%);
        background-attachment: fixed;
    }
    
    /* Add subtle glow effects */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 30%, rgba(30,200,184,0.15), transparent 60%),
            radial-gradient(circle at 80% 20%, rgba(139,92,246,0.12), transparent 60%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #0D1526 !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #9CA3AF !important;
    }
    
    /* Main title styling */
    h1 {
        background: linear-gradient(90deg, #1EC8B8 0%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    /* Subtitle */
    .subtitle {
        color: #9CA3AF;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Premium cards */
    [data-testid="stVerticalBlock"] > div:has(> div.element-container) {
        background: #161F33;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 
            0 10px 25px rgba(0,0,0,0.5),
            0 2px 6px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
    }
    
    /* Card hover effect */
    [data-testid="stVerticalBlock"] > div:has(> div.element-container):hover {
        transform: translateY(-3px);
        box-shadow: 
            0 15px 35px rgba(0,0,0,0.6),
            0 4px 10px rgba(0,0,0,0.5);
        border-color: rgba(255,255,255,0.1);
    }
    
    /* Info box styling */
    .stAlert {
        background: rgba(59,130,246,0.1) !important;
        border: 1px solid #3B82F6 !important;
        border-radius: 12px;
        color: #E5E7EB !important;
    }
    
    /* Success message */
    .stSuccess {
        background: rgba(34,197,94,0.1) !important;
        border: 1px solid #22C55E !important;
        border-radius: 12px;
        color: #E5E7EB !important;
    }
    
    /* Warning message */
    .stWarning {
        background: rgba(245,158,11,0.1) !important;
        border: 1px solid #F59E0B !important;
        border-radius: 12px;
        color: #E5E7EB !important;
    }
    
    /* Error message */
    .stError {
        background: rgba(239,68,68,0.1) !important;
        border: 1px solid #EF4444 !important;
        border-radius: 12px;
        color: #E5E7EB !important;
    }
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        background: #111B2E;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    
    /* Table header */
    [data-testid="stDataFrame"] thead tr {
        background: #1A253D !important;
    }
    
    [data-testid="stDataFrame"] th {
        color: #E5E7EB !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        padding: 12px !important;
    }
    
    /* Table rows */
    [data-testid="stDataFrame"] td {
        color: #D1D5DB !important;
        padding: 10px !important;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: #1A253D;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    
    [data-testid="stMetricValue"] {
        color: #1EC8B8 !important;
        font-weight: 700;
        font-size: 2rem;
    }
    
    [data-testid="stMetricLabel"] {
        color: #9CA3AF !important;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
        color: #9CA3AF;
        padding: 8px 20px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1EC8B8 0%, #8B5CF6 100%);
        color: #FFFFFF;
        border-color: transparent;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #1A253D;
        border: 2px dashed rgba(30,200,184,0.3);
        border-radius: 12px;
        padding: 2rem;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(30,200,184,0.6);
        background: #1F2A40;
    }
    
    /* Selectbox */
    [data-baseweb="select"] {
        background: #1A253D !important;
        border-radius: 8px !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: #0D1526 !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 8px !important;
    }
    
    /* Subheaders */
    h2, h3 {
        color: #E5E7EB !important;
        font-weight: 600;
    }
    
    /* Regular text */
    p, li, span {
        color: #D1D5DB;
    }
    
    /* Remove default streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1>Strategic Content Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Upload a real platform export CSV. We decode safely, detect platform by schema, and map into a standard dataset for analysis.</p>", unsafe_allow_html=True)

# Helper functions
def _metric_coverage(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for c in ["views", "impressions", "reach", "likes", "comments", "shares", "saves", "watch_time_seconds", "duration_seconds"]:
        if c not in df.columns:
            continue
        non_null = int(df[c].notna().sum())
        total = int(len(df))
        pct = round((non_null / total) * 100, 2) if total else 0.0
        rows.append({"metric": c, "non_null_rows": non_null, "total_rows": total, "coverage_percent": pct})
    return pd.DataFrame(rows)

def _text_preview(df: pd.DataFrame, col: str, n: int = 10) -> pd.DataFrame:
    if col not in df.columns:
        return pd.DataFrame()
    s = df[col].fillna("").astype(str)
    return pd.DataFrame({col: s.head(n)})

# Sidebar
with st.sidebar:
    st.header("Upload")
    platform_choice = st.selectbox(
        "Platform",
        ["Auto-detect", "YouTube", "LinkedIn", "Instagram", "TikTok"],
        index=0,
    )
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    
    st.markdown("")
    st.header("Tip")
    st.write("If you ever see weird symbols like ÐÑ or □□□ in text, that is a CSV encoding issue. This build fixes it during upload.")

# Main content
if uploaded is None:
    st.info("📤 Upload a CSV to begin.")
    st.stop()

choice_map = {
    "Auto-detect": "auto-detect",
    "YouTube": "youtube",
    "LinkedIn": "linkedin",
    "Instagram": "instagram",
    "TikTok": "tiktok",
}

file_bytes = uploaded.getvalue()

try:
    mapped_df, report = map_and_validate_csv(file_bytes, platform_choice=choice_map[platform_choice])
except TypeError as e:
    st.error("⚠️ Your schema.py function signature does not match what app.py is calling.")
    st.code(str(e))
    st.stop()
except Exception as e:
    st.error("❌ Could not read or map this CSV. Upload a valid export CSV.")
    st.code(str(e))
    st.stop()

st.success(f"✅ Loaded {report.rows:,} rows. Detected: **{report.detected_platform}**. Using: **{report.selected_platform}**.")

# Store in session
st.session_state["mapped_df"] = mapped_df
st.session_state["mapping_report"] = report

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Mapped Preview", "🔍 Mapping Report", "✅ Quality Checks"])

with tab1:
    st.subheader("Standardized dataset preview")
    st.dataframe(mapped_df.head(50), use_container_width=True, height=400)
    
    st.markdown("")
    st.subheader("Quick metrics summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(mapped_df):,}")
    c2.metric("Columns", f"{len(mapped_df.columns):,}")
    c3.metric("Non-empty titles", int(mapped_df["title"].notna().sum()))
    c4.metric("Non-empty captions", int(mapped_df["caption"].notna().sum()))

with tab2:
    st.subheader("What was mapped (source column → standard column)")
    mapped_pairs = [{"standard": k, "source": v} for k, v in report.mapped_columns.items()]
    st.dataframe(pd.DataFrame(mapped_pairs).sort_values("standard"), use_container_width=True, height=300)
    
    st.markdown("")
    st.subheader("Missing fields (why you see None)")
    if report.missing_standard_columns:
        st.warning("⚠️ These standard fields were not found in your CSV export, so they stay empty (NA).")
        st.write(report.missing_standard_columns)
    else:
        st.success("✅ All standard fields were present in the CSV.")
    
    st.markdown("")
    st.subheader("CSV decode and mapping notes")
    for n in report.notes:
        st.write(f"• {n}")
    
    st.markdown("")
    st.subheader("Original CSV columns seen")
    st.code(", ".join([str(c) for c in report.source_columns]))

with tab3:
    st.subheader("Metric coverage")
    cov = _metric_coverage(mapped_df)
    st.dataframe(cov, use_container_width=True, height=300)
    
    st.markdown("")
    st.subheader("Text sanity check")
    st.write("If text still looks corrupted, your file might not be a real platform export CSV, or it may be compressed/encoded strangely.")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Title preview**")
        st.dataframe(_text_preview(mapped_df, "title", 10), use_container_width=True)
    with c2:
        st.write("**Caption preview**")
        st.dataframe(_text_preview(mapped_df, "caption", 10), use_container_width=True)
    
    st.markdown("")
    st.subheader("Duplicate content check")
    if "caption" in mapped_df.columns:
        dup = mapped_df["caption"].fillna("").astype(str)
        dup_rate = round((dup.duplicated().sum() / max(len(dup), 1)) * 100, 2)
        st.write(f"Duplicate caption rate: **{dup_rate}%**")
        st.write("High duplication can be real for some datasets (like trending reposts), but if everything is identical, your mapping is pointing to the wrong column.")