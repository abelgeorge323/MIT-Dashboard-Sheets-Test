import pandas as pd
import streamlit as st
import plotly.express as px

# ---- PAGE CONFIG (must come FIRST) ----
st.set_page_config(
    page_title="MIT Candidate Training Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- FORCE DARK MODE ----
st.markdown("""<style>
:root, html[data-theme="light"], html[data-theme="dark"] {
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
[data-testid="stMetric"], [data-testid="stDataFrame"], [data-testid="stExpander"],
[data-testid="stPlotlyChart"], [data-testid="stHorizontalBlock"] {
    background-color: var(--secondary-bg-color) !important;
    color: var(--text-color) !important;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
}
.js-plotly-plot, .plot-container, canvas, svg { background-color: transparent !important; color: var(--text-color) !important; }
.plotly .main-svg { background-color: transparent !important; }
.plotly .bg { fill: transparent !important; }
.plotly .hovertext {
    background-color: #1a1d27 !important;
    color: #ffffff !important;
    border: 1px solid #4a4e5a !important;
    border-radius: 4px !important;
}
h1, h2, h3 { color: #dbe3f0 !important; text-align: center; font-weight: 700; text-shadow: none !important; }
table, th, td { background-color: #171b24 !important; color: #e1e1e1 !important; }
div[data-testid="stMetric"]:hover { box-shadow: 0 0 12px rgba(74,168,224,0.25); transform: translateY(-1px); transition: 0.3s ease; }
[data-testid="stExpander"]:hover { box-shadow: none !important; transform: none !important; transition: none !important; }
[data-testid="stExpander"] div, [data-testid="stExpander"] p, [data-testid="stExpander"] span,
[data-testid="stExpander"] strong, [data-testid="stExpander"] markdown, [data-testid="stExpander"] .stMarkdown {
    color: #e0e0e0 !important; background-color: transparent !important;
}
[data-testid="stExpander"] > div { background-color: var(--secondary-bg-color) !important; }
* { scrollbar-color: #333 #0e1016 !important; }
button, select, input, textarea {
    background-color: #1a1d27 !important; color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
button:hover { background-color: #26304a !important; }
a, svg, label { color: #70b8ff !important; }
[data-testid="stHeadingContainer"] h1 + div { display: none !important; }
</style>""", unsafe_allow_html=True)

st.markdown("<h1>🎓 MIT Candidate Training Dashboard</h1>", unsafe_allow_html=True)

# ---- LOAD DATA ----
@st.cache_data(ttl=300)
def load_data():
    main_data_url = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vSbD6wUrZEt9kuSQpUT2pw0FMOb7h1y8xeX-hDTeiiZUPjtV0ohK_WcFtCSt_4nuxdtn9zqFS8z8aGw/"
        "pub?gid=1155015355&single=true&output=csv"
    )
    try:
        df = pd.read_csv(main_data_url, skiprows=4)
        data_source = "Google Sheets"
    except Exception as e:
        st.error(f"⚠️ Google Sheets error: {e}")
        return pd.DataFrame(), "Error"

    df = df.dropna(how="all")
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    df = df.rename(columns={"Week ": "Week", "Start date": "Start Date"})
    if "Start Date" in df.columns:
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")

    today = pd.Timestamp.now()

    def calc_weeks(row):
        start = row["Start Date"]
        if pd.isna(start):
            return None
        if start > today:
            return f"-{int((start - today).days / 7)} weeks from start"
        return int(((today - start).days // 7) + 1)

    df["Week"] = df.apply(calc_weeks, axis=1)
    df["Week"] = pd.to_numeric(df["Week"], errors="coerce")

    if "Salary" in df.columns:
        df["Salary"] = (
            df["Salary"].astype(str)
            .str.replace("$", "")
            .str.replace(",", "")
            .str.replace(" ", "")
        )
        df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")

    df["Status"] = df["Status"].astype(str).str.strip().str.lower()
    return df, data_source


@st.cache_data(ttl=300)
def load_jobs_data():
    jobs_url = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vSbD6wUrZEt9kuSQpUT2pw0FMOb7h1y8xeX-hDTeiiZUPjtV0ohK_WcFtCSt_4nuxdtn9zqFS8z8aGw/"
        "pub?gid=116813539&single=true&output=csv"
    )
    try:
        jobs_df = pd.read_csv(jobs_url, skiprows=5, header=0)
        jobs_df = jobs_df.loc[:, ~jobs_df.columns.str.contains("^Unnamed")]
        jobs_df = jobs_df.drop(columns=[c for c in ["JV Link", "JV ID"] if c in jobs_df.columns], errors="ignore")
        jobs_df = jobs_df.dropna(how="all").fillna("")
        return jobs_df
    except Exception as e:
        st.error(f"Error loading jobs data: {e}")
        return pd.DataFrame()

# ---- LOAD ----
st.cache_data.clear()
df, data_source = load_data()
jobs_df = load_jobs_data()

if df.empty:
    st.error("❌ Unable to load data.")
    st.stop()

# ---- HEADER ----
st.markdown('<div class="dashboard-title">🎓 MIT Candidate Training Dashboard</div>', unsafe_allow_html=True)
if data_source == "Google Sheets":
    st.success(f"📊 Data Source: {data_source} | Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---- METRICS ----
offer_pending = len(df[df["Status"] == "offer pending"])
offer_accepted = len(df[df["Status"] == "offer accepted"])
non_identified = len(df[df["Status"].isin(["free agent discussing opportunity", "unassigned", "training"])])
total_candidates = non_identified + offer_accepted

ready_for_placement = df[
    df["Week"].apply(lambda x: isinstance(x, (int, float)) and x > 6)
    & (~df["Status"].isin(["position identified", "offer pending", "offer accepted"]))
]
ready = len(ready_for_placement)

in_training = len(
    df[df["Status"].eq("training") & df["Week"].apply(lambda x: isinstance(x, (int, float)) and x <= 6)]
)
open_jobs = len(jobs_df) if not jobs_df.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Candidates", total_candidates)
col2.metric("Open Positions", open_jobs)
col3.metric("Ready for Placement", ready)
col4.metric("In Training (Weeks 1–5)", in_training)
col5.metric("Offer Pending", offer_pending)

# ==========================================================
# 📊 TRAINING PROGRESS OVERVIEW (New Replacement Chart)
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
    pl
