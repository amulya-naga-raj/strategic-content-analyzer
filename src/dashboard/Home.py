import streamlit as st

st.set_page_config(
    page_title="Strategic Content Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; box-sizing: border-box; margin: 0; padding: 0; }

.stApp {
    background: linear-gradient(135deg, #0B1220 0%, #111B2E 100%);
    background-attachment: fixed;
    min-height: 100vh;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background:
        radial-gradient(circle at 15% 25%, rgba(30,200,184,0.15), transparent 50%),
        radial-gradient(circle at 85% 15%, rgba(139,92,246,0.12), transparent 50%),
        radial-gradient(circle at 50% 85%, rgba(59,130,246,0.07), transparent 45%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebarNav"],
[data-testid="stDecoration"],
#MainMenu, footer, header { display: none !important; }

.block-container {
    padding: 2.5rem 2rem 3rem !important;
    max-width: 100% !important;
    position: relative;
    z-index: 1;
}

/* ── HERO ── */
.hero-wrap {
    text-align: center;
    margin-bottom: 2.5rem;
    padding: 0 1rem;
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(30,200,184,0.08);
    border: 1px solid rgba(30,200,184,0.25);
    color: #1EC8B8;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 6px 18px;
    border-radius: 999px;
    margin-bottom: 1.5rem;
}

.hero-title {
    font-size: clamp(2rem, 4vw, 3.8rem);
    font-weight: 700;
    line-height: 1.12;
    color: #F9FAFB;
    margin-bottom: 1rem;
    letter-spacing: -0.02em;
}

.hero-title .gradient-text {
    background: linear-gradient(90deg, #1EC8B8 0%, #8B5CF6 60%, #3B82F6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    color: #6B7280;
    font-size: clamp(0.9rem, 1.5vw, 1.05rem);
    line-height: 1.75;
    max-width: 580px;
    margin: 0 auto 2rem;
}

/* ── BADGES ── */
.badges-row {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 2.5rem;
    padding: 0 1rem;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
    border: 1px solid;
    white-space: nowrap;
}

.badge-teal   { background: rgba(30,200,184,0.08);  border-color: rgba(30,200,184,0.25);  color: #1EC8B8; }
.badge-purple { background: rgba(139,92,246,0.08);  border-color: rgba(139,92,246,0.25);  color: #8B5CF6; }
.badge-amber  { background: rgba(245,158,11,0.08);  border-color: rgba(245,158,11,0.25);  color: #F59E0B; }
.badge-blue   { background: rgba(59,130,246,0.08);  border-color: rgba(59,130,246,0.25);  color: #60A5FA; }
.badge-gray   { background: rgba(156,163,175,0.08); border-color: rgba(156,163,175,0.2);  color: #9CA3AF; }

/* ── STATS ── */
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 2.5rem;
}

.stat-cell {
    background: rgba(255,255,255,0.02);
    padding: 1.25rem 1rem;
    text-align: center;
}

.stat-num {
    font-size: clamp(1.4rem, 2.5vw, 2rem);
    font-weight: 700;
    color: #F9FAFB;
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 0.3rem;
}

.stat-label {
    font-size: 0.7rem;
    font-weight: 500;
    color: #4B5563;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── SECTION HEADER ── */
.section-header {
    font-size: 0.68rem;
    font-weight: 600;
    color: #374151;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin-bottom: 1rem;
    padding: 0 0.25rem;
}

/* ── MODULE CARDS ── */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1rem;
}

.module-card {
    background: #131C2E;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 1.75rem 1.5rem;
    position: relative;
    overflow: hidden;
    min-height: 240px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

.module-card::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 140px; height: 140px;
    border-radius: 50%;
    opacity: 0.3;
}

.card-teal::before   { background: radial-gradient(circle, #1EC8B8, transparent 70%); }
.card-purple::before { background: radial-gradient(circle, #8B5CF6, transparent 70%); }
.card-amber::before  { background: radial-gradient(circle, #F59E0B, transparent 70%); }

.card-module-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4B5563;
    background: rgba(255,255,255,0.05);
    display: inline-block;
    padding: 3px 9px;
    border-radius: 5px;
    margin-bottom: 1rem;
}

.card-icon {
    font-size: 2rem;
    margin-bottom: 0.6rem;
    line-height: 1;
}

.card-title {
    font-size: clamp(1.1rem, 2vw, 1.45rem);
    font-weight: 700;
    color: #E5E7EB;
    margin-bottom: 0.6rem;
    letter-spacing: -0.01em;
}

.card-desc {
    color: #6B7280;
    font-size: 0.87rem;
    line-height: 1.6;
    flex-grow: 1;
    margin-bottom: 1.25rem;
}

.card-accent-line {
    height: 2px;
    border-radius: 999px;
    width: 36px;
    margin-top: auto;
}

.accent-teal   { background: #1EC8B8; }
.accent-purple { background: #8B5CF6; }
.accent-amber  { background: #F59E0B; }

/* ── PIPELINE CARD ── */
.pipeline-wrap {
    background: linear-gradient(135deg, #131C2E 0%, #1A253D 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 2.25rem 2rem;
    position: relative;
    overflow: hidden;
    text-align: center;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
    margin-bottom: 1rem;
}

.pipeline-wrap::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(30,200,184,0.12), rgba(139,92,246,0.1), transparent 65%);
    border-radius: 50%;
}

.pipeline-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #4B5563;
    background: rgba(255,255,255,0.05);
    display: inline-block;
    padding: 4px 12px;
    border-radius: 5px;
    margin-bottom: 1rem;
    position: relative;
    z-index: 1;
}

.pipeline-title {
    font-size: clamp(1.4rem, 3vw, 2rem);
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 0.6rem;
    letter-spacing: -0.02em;
    position: relative;
    z-index: 1;
}

.pipeline-desc {
    color: #6B7280;
    font-size: 0.95rem;
    line-height: 1.7;
    max-width: 480px;
    margin: 0 auto 1.5rem;
    position: relative;
    z-index: 1;
}

.pipeline-steps {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 1.75rem;
    position: relative;
    z-index: 1;
}

.step-pill {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    color: #9CA3AF;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 5px 12px;
    border-radius: 6px;
    white-space: nowrap;
}

.step-arrow {
    color: #374151;
    font-size: 0.9rem;
    padding: 0 4px;
}

/* ── BUTTONS ── */
div.stButton > button {
    background: linear-gradient(135deg, #1EC8B8 0%, #3B82F6 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 11px 24px;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.01em;
    transition: all 0.25s ease;
    box-shadow: 0 4px 14px rgba(30,200,184,0.28);
    width: 100%;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(30,200,184,0.38);
}

/* ── FOOTER ── */
.footer-note {
    text-align: center;
    color: #374151;
    font-size: 0.78rem;
    margin-top: 1.5rem;
    padding-top: 1.25rem;
    border-top: 1px solid rgba(255,255,255,0.04);
}
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">⚡ Trust &amp; Safety Intelligence Platform</div>
    <div class="hero-title">
        Strategic Content<br>
        <span class="gradient-text">Analyzer</span>
    </div>
    <div class="hero-sub">
        Production-grade content intelligence built from a Trust &amp; Safety perspective.
        Predicts engagement with explainable AI and detects artificial manipulation signals
        across social media platforms.
    </div>
</div>
""", unsafe_allow_html=True)

# ── BADGES ────────────────────────────────────────
st.markdown("""
<div class="badges-row">
    <span class="badge badge-teal">● Explainable AI</span>
    <span class="badge badge-purple">● Manipulation Detection</span>
    <span class="badge badge-amber">● Cross-platform Intelligence</span>
    <span class="badge badge-blue">● Isolation Forest + Rules</span>
    <span class="badge badge-gray">● No Scraping · No APIs</span>
</div>
""", unsafe_allow_html=True)

# ── STATS ─────────────────────────────────────────
st.markdown("""
<div class="stats-row">
    <div class="stat-cell">
        <div class="stat-num">500K+</div>
        <div class="stat-label">Data Points</div>
    </div>
    <div class="stat-cell">
        <div class="stat-num">~87%</div>
        <div class="stat-label">Prediction Accuracy</div>
    </div>
    <div class="stat-cell">
        <div class="stat-num">4</div>
        <div class="stat-label">Platforms</div>
    </div>
    <div class="stat-cell">
        <div class="stat-num">Real-time</div>
        <div class="stat-label">Detection Engine</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── MODULE CARDS ──────────────────────────────────
st.markdown('<div class="section-header">— Core Modules</div>', unsafe_allow_html=True)

st.markdown("""
<div class="cards-grid">
    <div class="module-card card-teal">
        <div class="card-module-label">Module · Predict</div>
        <div class="card-icon">🔮</div>
        <div class="card-title">Engagement Prediction</div>
        <div class="card-desc">
            Predict likes, comments, and views using Random Forest trained on
            real platform datasets with robust feature pipelines.
        </div>
        <div class="card-accent-line accent-teal"></div>
    </div>
    <div class="module-card card-purple">
        <div class="card-module-label">Module · Explain</div>
        <div class="card-icon">🧠</div>
        <div class="card-title">Explainable AI</div>
        <div class="card-desc">
            Transparent "why" behind every prediction using permutation-based
            feature attribution and top driver breakdowns. No black boxes.
        </div>
        <div class="card-accent-line accent-purple"></div>
    </div>
    <div class="module-card card-amber">
        <div class="card-module-label">Module · Detect</div>
        <div class="card-icon">🛡️</div>
        <div class="card-title">Manipulation Detection</div>
        <div class="card-desc">
            Flag suspicious spikes, abnormal like/comment ratios, and bot
            patterns using Isolation Forest + rule-based signals. Scored 0–100.
        </div>
        <div class="card-accent-line accent-amber"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── MODULE BUTTONS ────────────────────────────────
b1, b2, b3 = st.columns(3)
with b1:
    if st.button("Open Predict →", key="btn_predict"):
        st.switch_page("pages/1_Predict.py")
with b2:
    if st.button("Open Explain →", key="btn_explain"):
        st.switch_page("pages/2_Explain.py")
with b3:
    if st.button("Open Detect →", key="btn_detect"):
        st.switch_page("pages/3_Detect.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── PIPELINE CARD ─────────────────────────────────
st.markdown('<div class="section-header">— Full Analysis Pipeline</div>', unsafe_allow_html=True)

st.markdown("""
<div class="pipeline-wrap">
    <div class="pipeline-label">Pipeline</div>
    <div class="pipeline-title">Start Full Analysis</div>
    <div class="pipeline-desc">
        Upload any real social media export CSV. It will standardize the schema,
        run ML predictions, explain them, and flag manipulation.
    </div>
    <div class="pipeline-steps">
        <span class="step-pill">📁 Upload CSV</span>
        <span class="step-arrow">→</span>
        <span class="step-pill">🔄 Standardize</span>
        <span class="step-arrow">→</span>
        <span class="step-pill">🔮 Predict</span>
        <span class="step-arrow">→</span>
        <span class="step-pill">🧠 Explain</span>
        <span class="step-arrow">→</span>
        <span class="step-pill">🛡️ Detect</span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("Launch Full Analysis →", key="btn_analysis"):
    st.switch_page("pages/0_Analysis.py")

# ── FOOTER ────────────────────────────────────────
st.markdown("""
<div class="footer-note">
    Amulya Naga Raj &nbsp;·&nbsp; M.S. Computer Science &nbsp;·&nbsp; Syracuse University
    &nbsp;·&nbsp; AI-Powered Intelligence
    &nbsp;·&nbsp; Built for Trust &amp; Safety Engineering Roles
</div>
""", unsafe_allow_html=True)
