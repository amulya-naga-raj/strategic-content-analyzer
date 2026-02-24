import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from src.data_processing.schema import generate_sample_data
from src.models.models import ManipulationDetector

st.set_page_config(page_title="Detect — SCA", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

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
.metric-val-red   { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 700; color: #EF4444; }
.metric-val-green { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 700; color: #22C55E; }
.metric-val       { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 700; color: #F59E0B; }
.metric-lbl { font-size: 0.78rem; color: #475569; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.25rem; }
.stButton > button { background: rgba(239,68,68,0.12) !important; color: #EF4444 !important; border: 1px solid rgba(239,68,68,0.35) !important; border-radius: 8px !important; font-family: 'Syne', sans-serif !important; font-weight: 600 !important; }
.signal-tag { display: inline-block; background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.3); color: #EF4444; border-radius: 6px; padding: 0.2rem 0.6rem; font-size: 0.75rem; margin: 0.15rem; }
.clean-tag  { display: inline-block; background: rgba(34,197,94,0.10);  border: 1px solid rgba(34,197,94,0.3);  color: #22C55E; border-radius: 6px; padding: 0.2rem 0.6rem; font-size: 0.75rem; }
</style>
""", unsafe_allow_html=True)

if st.button("← Home"):
    st.switch_page("Home.py")

st.markdown('<div class="page-title">🛡️ Manipulation Detection</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Isolation Forest + rule-based signals detect artificial engagement. Each post scored 0–100 for authenticity.</div>', unsafe_allow_html=True)

df = st.session_state.get("df", None)
if df is None:
    df = generate_sample_data("YouTube", 200)
    st.session_state["df"] = df

if st.button("🔍 Run Manipulation Detection"):
    with st.spinner("Running detection..."):
        detector = ManipulationDetector().fit(df)
        result_df = detector.predict(df)
        st.session_state["detect_df"] = result_df
    st.success("✅ Detection complete!")

result_df = st.session_state.get("detect_df", None)
if result_df is None:
    st.info("👆 Click 'Run Manipulation Detection' to analyze.")
    st.stop()

flagged   = result_df["manipulation_flag"].sum()
clean     = len(result_df) - flagged
avg_auth  = result_df["authenticity_score"].mean()
high_risk = (result_df["authenticity_score"] < 40).sum()

st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="metric-card"><div class="metric-val-red">{flagged}</div><div class="metric-lbl">Flagged Posts</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-card"><div class="metric-val-green">{clean}</div><div class="metric-lbl">Clean Posts</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-card"><div class="metric-val">{avg_auth:.1f}</div><div class="metric-lbl">Avg Authenticity</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-card"><div class="metric-val-red">{high_risk}</div><div class="metric-lbl">High Risk (&lt;40)</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Overview", "🗺️ Anomaly Map", "📋 Flagged Posts"])

with tab1:
    v1, v2 = st.columns(2)
    with v1:
        fig = px.histogram(result_df, x="authenticity_score", nbins=30,
            title="Authenticity Score Distribution", color_discrete_sequence=["#14B8A6"])
        fig.add_vline(x=40, line_dash="dash", line_color="#EF4444",
            annotation_text="Risk Threshold", annotation_font_color="#EF4444")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#94A3B8", title_font_color="#E2E8F0")
        st.plotly_chart(fig, use_container_width=True)
    with v2:
        fig2 = px.pie(pd.DataFrame({"Status":["Clean","Flagged"],"Count":[clean,flagged]}),
            names="Status", values="Count", title="Content Integrity",
            color_discrete_map={"Clean":"#22C55E","Flagged":"#EF4444"}, hole=0.5)
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#94A3B8", title_font_color="#E2E8F0")
        st.plotly_chart(fig2, use_container_width=True)

    from collections import Counter
    all_signals = []
    for s in result_df["signals"]: all_signals.extend(s)
    if all_signals:
        sig_df = pd.DataFrame(Counter(all_signals).items(), columns=["Signal","Count"]).sort_values("Count")
        fig3 = px.bar(sig_df, x="Count", y="Signal", orientation="h",
            title="Most Common Signals", color_discrete_sequence=["#EF4444"])
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#94A3B8", title_font_color="#E2E8F0")
        st.plotly_chart(fig3, use_container_width=True)

with tab2:
    fig4 = px.scatter(result_df, x="likes", y="comments", color="manipulation_flag",
        size="authenticity_score", color_discrete_map={True:"#EF4444",False:"#14B8A6"},
        title="Likes vs Comments — Anomaly Map", opacity=0.7,
        hover_data=["authenticity_score","anomaly_score"])
    fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#94A3B8", title_font_color="#E2E8F0", height=500)
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    flagged_df = result_df[result_df["manipulation_flag"] == True].copy()
    if flagged_df.empty:
        st.success("✅ No manipulation detected.")
    else:
        display_cols = [c for c in ["post_id","date","views","likes","comments","engagement_rate","authenticity_score","anomaly_score","signal_count"] if c in flagged_df.columns]
        st.dataframe(flagged_df[display_cols].sort_values("authenticity_score").head(50), use_container_width=True, height=400)

        st.markdown("#### Signal Breakdown (Top 10 worst)")
        for i, (_, row) in enumerate(flagged_df.sort_values("authenticity_score").head(10).iterrows()):
            with st.expander(f"Post {row.get('post_id','#'+str(i))} — Authenticity: {row['authenticity_score']:.0f}/100"):
                s1, s2, s3 = st.columns(3)
                s1.metric("Views",    f"{int(row['views']):,}")
                s2.metric("Likes",    f"{int(row['likes']):,}")
                s3.metric("Comments", f"{int(row['comments']):,}")
                if row["signals"]:
                    tags = " ".join([f'<span class="signal-tag">⚠ {s}</span>' for s in row["signals"]])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.markdown('<span class="clean-tag">✓ Flagged by Isolation Forest only</span>', unsafe_allow_html=True)
