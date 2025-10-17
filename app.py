import pandas as pd
import streamlit as st
import plotly.express as px

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="MIT Candidate Training Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- FORCE DARK MODE ----
st.markdown("""
<style>
:root,
html[data-theme="light"],
html[data-theme="dark"] {
    color-scheme: dark !important;
    --background-color: #0e1016 !important;
    --text-color: #e0e0e0 !important;
    --secondary-bg-color: #151820 !important;
    --primary-color: #4aa8e0 !important;
}
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
}
[data-testid="stMetric"], [data-testid="stDataFrame"], [data-testid="stExpander"], [data-testid="stPlotlyChart"] {
    background-color: var(--secondary-bg-color) !important;
    color: var(--text-color) !important;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
}
h1, h2, h3 {
    color: #dbe3f0 !important;
    text-align: center;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ---- HEADER ----
st.markdown("<h1>🎓 MIT Candidate Training Dashboard</h1>", unsafe_allow_html=True)


# ---- LOAD DATA ----
@st.cache_data(ttl=300)
def load_data():
    url = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vSbD6wUrZEt9kuSQpUT2pw0FMOb7h1y8xeX-hDTeiiZUPjtV0ohK_WcFtCSt_4nuxdtn9zqFS8z8aGw/"
        "pub?gid=1155015355&single=true&output=csv"
    )
    df = pd.read_csv(url, skiprows=4)
    df = df.dropna(how="all")

    # Clean columns
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={"Start date": "Start Date", "Week ": "Week"})

    # Parse Start Date
    if "Start Date" in df.columns:
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")

    today = pd.Timestamp.now()

    def compute_week(row):
        start = row.get("Start Date", None)
        manual_week = row.get("Week", None)
        if pd.notna(start):
            diff = (today - start).days
            if diff >= 0:
                return int(diff // 7 + 1)
        # fallback if invalid date
        try:
            return int(manual_week)
        except Exception:
            return None

    df["Week"] = df.apply(compute_week, axis=1)
    df["Week"] = pd.to_numeric(df["Week"], errors="coerce")

    if "Status" in df.columns:
        df["Status"] = df["Status"].astype(str).str.lower().str.strip()

    return df


@st.cache_data(ttl=300)
def load_jobs_data():
    url = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vSbD6wUrZEt9kuSQpUT2pw0FMOb7h1y8xeX-hDTeiiZUPjtV0ohK_WcFtCSt_4nuxdtn9zqFS8z8aGw/"
        "pub?gid=116813539&single=true&output=csv"
    )
    try:
        jobs = pd.read_csv(url, skiprows=5)
        jobs = jobs.loc[:, ~jobs.columns.str.contains("^Unnamed")]
        return jobs.dropna(how="all")
    except Exception:
        return pd.DataFrame()


st.cache_data.clear()
df = load_data()
jobs_df = load_jobs_data()

if df.empty:
    st.error("❌ Could not load candidate data.")
    st.stop()

# ---- METRICS ----
offer_pending = len(df[df["Status"] == "offer pending"])
ready_for_placement = len(df[df["Week"] >= 7])
nearing_placement = len(df[(df["Week"] >= 5) & (df["Week"] <= 6)])
in_training = len(df[df["Week"] <= 4])
open_jobs = len(jobs_df)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Candidates", len(df))
col2.metric("Open Jobs", open_jobs)
col3.metric("Ready for Placement", ready_for_placement)
col4.metric("Nearing Placement", nearing_placement)
col5.metric("Offer Pending", offer_pending)

# ==========================================================
# 📊 TRAINING PROGRESS OVERVIEW (New Chart)
# ==========================================================
st.markdown("---")
st.subheader("📊 Candidate Training Progress Overview")

def classify_training_stage(week):
    if pd.isna(week):
        return "Unknown"
    elif week >= 7:
        return "Ready for Placement"
    elif 5 <= week <= 6:
        return "Nearing Placement"
    else:
        return "In Training"

df["Training Stage"] = df["Week"].apply(classify_training_stage)

progress_counts = (
    df["Training Stage"]
    .value_counts()
    .reindex(["In Training", "Nearing Placement", "Ready for Placement"])
    .fillna(0)
    .reset_index()
)
progress_counts.columns = ["Stage", "Count"]

color_map = {
    "In Training": "#E15F99",
    "Nearing Placement": "#F5A623",
    "Ready for Placement": "#2E91E5"
}

fig_progress = px.pie(
    progress_counts,
    names="Stage",
    values="Count",
    hole=0.45,
    color="Stage",
    color_discrete_map=color_map
)

fig_progress.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="white",
    height=400,
    legend=dict(font=dict(color="white", size=14)),
    hoverlabel=dict(bgcolor="#1a1d27", font_color="white", font_size=12)
)

st.plotly_chart(fig_progress, use_container_width=True)

# ==========================================================
# 🧩 READY FOR PLACEMENT TABLE
# ==========================================================
ready_df = df[df["Week"] >= 7]
if not ready_df.empty:
    st.markdown("---")
    st.markdown("### 🧩 Ready for Placement Candidates")
    st.dataframe(
        ready_df[["MIT Name", "Training Site", "Location", "Week"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.markdown('<div class="placeholder-box">No candidates ready for placement yet.</div>', unsafe_allow_html=True)

# ==========================================================
# 🏋️ IN TRAINING TABLE
# ==========================================================
training_df = df[df["Week"] <= 4]
if not training_df.empty:
    st.markdown("---")
    st.markdown("### 🏋️ In Training (Weeks 1–4)")
    st.dataframe(
        training_df[["MIT Name", "Training Site", "Location", "Week"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.markdown('<div class="placeholder-box">No current trainees in Weeks 1–4.</div>', unsafe_allow_html=True)
