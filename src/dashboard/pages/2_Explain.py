import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.data_processing.schema import generate_sample_data
from src.models.models import EngagementPredictor, Explainer

st.set_page_config(page_title="Explain — SCA", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")

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
.stButton > button { background: rgba(245,158,11,0.12) !important; color: #F59E0B !important; border: 1px solid rgba(245,158,11,0.35) !important; border-radius: 8px !important; font-family: 'Syne', sans-serif !important; font-weight: 600 !important; }
.explain-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; }
.feat-name { font-family: 'Syne', sans-serif; font-weight: 600; color: #E2E8F0; font-size: 0.95rem; }
.feat-val { color: #64748B; font-size: 0.82rem; margin-top: 0.15rem; }
</style>
""", unsafe_allow_html=True)

if st.button("← Home"):
    st.switch_page("Home.py")

st.markdown('<div class="page-title">🧠 Explainable AI</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Understand which features drive each prediction. No black boxes.</div>', unsafe_allow_html=True)

df = st.session_state.get("df", None)
if df is None:
    df = generate_sample_data("YouTube", 200)
    st.session_state["df"] = df

predictor = st.session_state.get("predictor", None)
if predictor is None:
    with st.spinner("Training model..."):
        predictor = EngagementPredictor().fit(df)
        st.session_state["predictor"] = predictor

explainer = Explainer(predictor)

st.markdown("### 🌍 Global Feature Importance")
global_imp = explainer.explain_global()
colors = ["#F59E0B" if i < 3 else "#334155" for i in range(len(global_imp))]
fig = go.Figure()
fig.add_trace(go.Bar(x=global_imp["importance"], y=global_imp["feature"], orientation="h",
    marker_color=colors, text=[f"{v:.4f}" for v in global_imp["importance"]],
    textposition="outside", textfont=dict(color="#64748B", size=11)))
fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color="#94A3B8", title_font_color="#E2E8F0",
    yaxis=dict(autorange="reversed"),
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
    height=420, margin=dict(l=0, r=60, t=20, b=20))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### 🔍 Explain a Single Post")

sample_row = st.session_state.get("sample_row", None)
if sample_row is not None:
    st.info("Using the post configured in the Predict page.")
    row_to_explain = sample_row
else:
    idx = st.slider("Select Post Index", 0, len(df)-1, 0)
    row_to_explain = df.iloc[idx]

with st.spinner("Computing contributions..."):
    contrib_df = explainer.explain_row(row_to_explain)

if contrib_df.empty:
    st.warning("Could not compute explanation.")
    st.stop()

pred_score = predictor.predict(pd.DataFrame([row_to_explain]))[0]
st.markdown(f"**Predicted Engagement Rate: `{pred_score:.2f}%`**")

contrib_sorted = contrib_df.head(10).copy()
colors2 = ["#14B8A6" if v >= 0 else "#EF4444" for v in contrib_sorted["contribution"]]
fig2 = go.Figure()
fig2.add_trace(go.Bar(x=contrib_sorted["contribution"], y=contrib_sorted["feature"], orientation="h",
    marker_color=colors2, text=[f"{v:+.4f}" for v in contrib_sorted["contribution"]],
    textposition="outside", textfont=dict(color="#94A3B8", size=11)))
fig2.update_layout(title="Feature Contributions", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color="#94A3B8", title_font_color="#E2E8F0", yaxis=dict(autorange="reversed"),
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
    height=380, margin=dict(l=0, r=60, t=50, b=20))
st.plotly_chart(fig2, use_container_width=True)

ic1, ic2 = st.columns(2)
with ic1:
    st.markdown("**✅ Positive Drivers**")
    for _, row in contrib_df[contrib_df["contribution"] > 0].head(3).iterrows():
        st.markdown(f'<div class="explain-card"><div class="feat-name">↑ {row["feature"]}</div><div class="feat-val">Value: {row["value"]:.4f} · Contribution: <span style="color:#14B8A6">+{row["contribution"]:.4f}</span></div></div>', unsafe_allow_html=True)
with ic2:
    st.markdown("**❌ Negative Drivers**")
    for _, row in contrib_df[contrib_df["contribution"] < 0].head(3).iterrows():
        st.markdown(f'<div class="explain-card"><div class="feat-name">↓ {row["feature"]}</div><div class="feat-val">Value: {row["value"]:.4f} · Contribution: <span style="color:#EF4444">{row["contribution"]:.4f}</span></div></div>', unsafe_allow_html=True)
