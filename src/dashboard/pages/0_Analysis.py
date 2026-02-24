import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_processing.schema import process_upload, generate_sample_data

st.set_page_config(page_title="Analysis — SCA", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
* { font-family: 'DM Sans', sans-serif; }
.stApp { background: #080C14; }
[data-testid="stSidebarNav"], header, footer { display: none !important; }
.block-container { padding: 2.5rem 4rem !important; max-width: 1200px; }
h1,h2,h3 { font-family: 'Syne', sans-serif !important; color: #E2E8F0 !important; }
.page-title { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: #E2E8F0; margin-bottom: 0.25rem; }
.page-sub { color: #475569; font-size: 0.95rem; margin-bottom: 2rem; }
.metric-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 1.25rem 1.5rem; text-align: center; }
.metric-val { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 700; color: #14B8A6; }
.metric-lbl { font-size: 0.78rem; color: #475569; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.25rem; }
.stButton > button { background: rgba(20,184,166,0.12) !important; color: #14B8A6 !important; border: 1px solid rgba(20,184,166,0.35) !important; border-radius: 8px !important; font-family: 'Syne', sans-serif !important; font-weight: 600 !important; }
.stTabs [data-baseweb="tab"] { color: #475569 !important; }
.stTabs [aria-selected="true"] { color: #14B8A6 !important; }
</style>
""", unsafe_allow_html=True)

if st.button("← Home"):
    st.switch_page("Home.py")

st.markdown('<div class="page-title">📊 Data Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Upload a platform CSV or use built-in demo data.</div>', unsafe_allow_html=True)

col_src, col_plat = st.columns([2, 1])
with col_src:
    data_source = st.radio("Data Source", ["Use Demo Data", "Upload CSV"], horizontal=True)
with col_plat:
    demo_platform = st.selectbox("Demo Platform", ["YouTube", "Instagram", "TikTok", "LinkedIn", "Twitter"])

df = None
mapping_report = {}

if data_source == "Use Demo Data":
    df = generate_sample_data(demo_platform, n=200)
    st.success(f"✅ Loaded 200 synthetic {demo_platform} posts (10% manipulation injected).")
    mapping_report = {"mapped": {c: "generated" for c in ["views","impressions","reach","likes","comments","shares","saves"]}, "missing": []}
else:
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        try:
            df, detected_platform, mapping_report = process_upload(uploaded.read())
            st.success(f"✅ Detected: **{detected_platform}** | {len(df)} rows loaded")
        except Exception as e:
            st.error(f"❌ Error: {e}")

if df is None:
    st.info("👆 Select a data source above to begin.")
    st.stop()

st.session_state["df"] = df

st.markdown("---")
c1, c2, c3, c4, c5 = st.columns(5)
for col, (lbl, val) in zip([c1,c2,c3,c4,c5], [
    ("Total Posts", len(df)),
    ("Avg Views", f"{int(df['views'].mean()):,}"),
    ("Avg Engagement", f"{df['engagement_rate'].mean():.2f}%"),
    ("Flagged Posts", int(df['manipulation_flag'].sum())),
    ("Avg Authenticity", f"{df['authenticity_score'].mean():.1f}/100"),
]):
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📋 Data Preview", "📈 Visualizations", "🗺️ Mapping Report"])

with tab1:
    st.dataframe(df.head(50), use_container_width=True, height=400)

with tab2:
    v1, v2 = st.columns(2)
    with v1:
        fig = px.histogram(df, x="engagement_rate", nbins=40, title="Engagement Rate Distribution", color_discrete_sequence=["#14B8A6"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#94A3B8", title_font_color="#E2E8F0")
        st.plotly_chart(fig, use_container_width=True)
    with v2:
        fig2 = px.scatter(df[df["views"] < df["views"].quantile(0.99)], x="views", y="engagement_rate",
            color="manipulation_flag", color_discrete_map={True:"#EF4444", False:"#14B8A6"},
            title="Views vs Engagement Rate", opacity=0.6)
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#94A3B8", title_font_color="#E2E8F0")
        st.plotly_chart(fig2, use_container_width=True)
    try:
        ts = df.copy()
        ts["date"] = pd.to_datetime(ts["date"])
        ts = ts.groupby("date")["views"].sum().reset_index()
        fig3 = px.line(ts, x="date", y="views", title="Views Over Time", color_discrete_sequence=["#7C3AED"])
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#94A3B8", title_font_color="#E2E8F0")
        st.plotly_chart(fig3, use_container_width=True)
    except Exception:
        pass

with tab3:
    if mapping_report.get("mapped"):
        st.dataframe(pd.DataFrame(list(mapping_report["mapped"].items()), columns=["Standard Metric","Source Column"]), use_container_width=True)
    if mapping_report.get("missing"):
        st.warning(f"Missing fields: {', '.join(mapping_report['missing'])}")

st.markdown("---")
st.markdown("*Use the sidebar to navigate to Predict → Explain → Detect*")
