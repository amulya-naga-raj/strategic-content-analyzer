import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data_processing.schema import generate_sample_data
from src.models.models import EngagementPredictor

st.set_page_config(page_title="Predict — SCA", page_icon="🔮", layout="wide", initial_sidebar_state="collapsed")

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
.metric-val { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 700; color: #8B5CF6; }
.metric-lbl { font-size: 0.78rem; color: #475569; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.25rem; }
.stButton > button { background: rgba(139,92,246,0.12) !important; color: #8B5CF6 !important; border: 1px solid rgba(139,92,246,0.35) !important; border-radius: 8px !important; font-family: 'Syne', sans-serif !important; font-weight: 600 !important; }
.score-box { background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(20,184,166,0.10)); border: 1px solid rgba(139,92,246,0.3); border-radius: 16px; padding: 2rem; text-align: center; }
.score-num { font-family: 'Syne', sans-serif; font-size: 4rem; font-weight: 800; background: linear-gradient(135deg, #8B5CF6, #14B8A6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""", unsafe_allow_html=True)

if st.button("← Home"):
    st.switch_page("Home.py")

st.markdown('<div class="page-title">🔮 Engagement Prediction</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Random Forest model predicts engagement rate. Train then predict any post.</div>', unsafe_allow_html=True)

df = st.session_state.get("df", None)
if df is None:
    st.warning("⚠️ No data loaded. Using YouTube demo data.")
    df = generate_sample_data("YouTube", 200)
    st.session_state["df"] = df

if st.button("🚀 Train Prediction Model"):
    with st.spinner("Training Random Forest..."):
        predictor = EngagementPredictor().fit(df)
        st.session_state["predictor"] = predictor
    st.success(f"✅ Model trained! R² score: {predictor.score(df):.4f}")

predictor = st.session_state.get("predictor", None)
if predictor is None:
    st.info("👆 Click 'Train Prediction Model' to get started.")
    st.stop()

df_pred = df.copy()
df_pred["predicted_engagement"] = predictor.predict(df).round(2)
df_pred["prediction_error"] = (df_pred["predicted_engagement"] - df_pred["engagement_rate"]).round(2)

st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
for col, (lbl, val) in zip([c1,c2,c3,c4], [
    ("R² Score", f"{predictor.score(df):.4f}"),
    ("Mean Predicted", f"{df_pred['predicted_engagement'].mean():.2f}%"),
    ("Mean Actual", f"{df_pred['engagement_rate'].mean():.2f}%"),
    ("Mean Error", f"{df_pred['prediction_error'].abs().mean():.2f}%"),
]):
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{val}</div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

ch1, ch2 = st.columns(2)
with ch1:
    fig = px.scatter(df_pred, x="engagement_rate", y="predicted_engagement",
        title="Actual vs Predicted", color_discrete_sequence=["#8B5CF6"], opacity=0.6)
    max_val = max(df_pred["engagement_rate"].max(), df_pred["predicted_engagement"].max())
    fig.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="#14B8A6", dash="dash", width=1))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#94A3B8", title_font_color="#E2E8F0")
    st.plotly_chart(fig, use_container_width=True)

with ch2:
    imp_df = predictor.feature_importance().head(10)
    fig2 = px.bar(imp_df, x="importance", y="feature", orientation="h", title="Feature Importance",
        color="importance", color_continuous_scale=["#1E293B","#8B5CF6"])
    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#94A3B8",
        title_font_color="#E2E8F0", yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.markdown("### 🎯 Predict a Single Post")

sc1, sc2, sc3 = st.columns(3)
with sc1:
    views      = st.slider("Views",       100, 500_000, 50_000,  step=1000)
    impressions= st.slider("Impressions", 100, 1_000_000, 100_000, step=1000)
    reach      = st.slider("Reach",       100, 500_000, 60_000,  step=1000)
with sc2:
    likes    = st.slider("Likes",    0, 100_000, 2_000, step=100)
    comments = st.slider("Comments", 0,  10_000,   150, step=10)
    shares   = st.slider("Shares",   0,  50_000,   300, step=50)
with sc3:
    saves      = st.slider("Saves",            0,  20_000,  200, step=50)
    watch_time = st.slider("Watch Time (min)", 0, 500_000, 10_000, step=500)
    duration   = st.slider("Duration (sec)",  10,   3600,   300, step=10)

sample_row = pd.DataFrame([{
    "views": views, "impressions": impressions, "reach": reach,
    "likes": likes, "comments": comments, "shares": shares,
    "saves": saves, "watch_time": watch_time, "duration": duration,
    "engagement_rate": (likes + comments + shares) / max(views, 1) * 100,
    "authenticity_score": 80, "manipulation_flag": False,
}])

pred_val   = predictor.predict(sample_row)[0]
actual_val = sample_row["engagement_rate"].iloc[0]
level = "🔥 Viral" if pred_val > 10 else "✅ Good" if pred_val > 3 else "⚠️ Below Average" if pred_val > 1 else "❌ Low"

rc1, rc2, rc3 = st.columns(3)
with rc1:
    st.markdown(f'<div class="score-box"><div class="score-num">{pred_val:.1f}%</div><div style="color:#64748B;font-size:0.85rem;margin-top:0.5rem;">Predicted Engagement</div></div>', unsafe_allow_html=True)
with rc2:
    st.markdown(f'<div class="score-box"><div class="score-num">{actual_val:.1f}%</div><div style="color:#64748B;font-size:0.85rem;margin-top:0.5rem;">Calculated Engagement</div></div>', unsafe_allow_html=True)
with rc3:
    st.markdown(f'<div class="score-box" style="padding:2.5rem;"><div style="font-family:Syne,sans-serif;font-size:2rem;font-weight:800;color:#E2E8F0;">{level}</div><div style="color:#64748B;font-size:0.85rem;margin-top:0.5rem;">Engagement Level</div></div>', unsafe_allow_html=True)

st.session_state["sample_row"] = sample_row.iloc[0]
