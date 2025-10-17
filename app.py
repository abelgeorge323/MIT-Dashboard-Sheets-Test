import pandas as pd
import streamlit as st
import plotly.express as px

# ---- PAGE CONFIG (must come FIRST) ----
st.set_page_config(
    page_title="MIT Candidate Training Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- FORCE DARK MODE ACROSS ALL BROWSERS ----
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
[data-testid="stMetric"],
[data-testid="stDataFrame"],
[data-testid="stExpander"],
[data-testid="stPlotlyChart"],
[data-testid="stHorizontalBlock"] {
    background-color: var(--secondary-bg-color) !important;
    color: var(--text-color) !important;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
}
.js-plotly-plot, .plot-container, canvas, svg {
    background-color: transparent !important;
    color: var(--text-color) !important;
}
.plotly .main-svg {
    background-color: transparent !important;
}
.plotly .bg {
    fill: transparent !important;
}
.plotly .hovertext {
    background-color: #1a1d27 !important;
    color: #ffffff !important;
    border: 1px solid #4a4e5a !important;
    border-radius: 4px !important;
}
h1, h2, h3 {
    color: #dbe3f0 !important;
    text-align: center;
    font-weight: 700;
    text-shadow: none !important;
}
table, th, td {
    background-color: #171b24 !important;
    color: #e1e1e1 !important;
}
div[data-testid="stMetric"]:hover {
    box-shadow: 0 0 12px rgba(74,168,224,0.25);
    transform: translateY(-1px);
    transition: 0.3s ease;
}
[data-testid="stExpander"]:hover {
    box-shadow: none !important;
    transform: none !important;
    transition: none !important;
}
[data-testid="stExpander"] div,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span,
[data-testid="stExpander"] strong,
[data-testid="stExpander"] markdown,
[data-testid="stExpander"] .stMarkdown {
    color: #e0e0e0 !important;
    background-color: transparent !important;
}
[data-testid="stExpander"] > div {
    background-color: var(--secondary-bg-color) !important;
}
* {
    scrollbar-color: #333 #0e1016 !important;
}
button, select, input, textarea {
    background-color: #1a1d27 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
button:hover {
    background-color: #26304a !important;
}
a, svg, label {
    color: #70b8ff !important;
}
[data-testid="stHeadingContainer"] h1 + div {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1>🎓 MIT Candidate Training Dashboard</h1>", unsafe_allow_html=True)

# ---- CUSTOM STYLING ----
st.markdown("""
    <style>
        :root {
            color-scheme: dark;
        }
        body, .stApp {
            background-color: #0b0e14 !important;
            color: #f5f5f5 !important;
        }
        h1, h2, h3, h4, h5, h6, p, span, div {
            color: #f5f5f5 !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 1rem !important;
            color: #bbbbbb !important;
        }
        .stMetric {
            background: #15181e !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 0 15px rgba(108, 99, 255, 0.15);
            text-align: center;
        }
        .data-source {
            background-color: #143d33;
            padding: 12px 18px;
            border-radius: 10px;
            font-weight: 500;
            color: #e1e1e1;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
        }
        [data-testid="stDataFrame"] {
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 0 10px rgba(108, 99, 255, 0.15);
        }
        table {
            background-color: #14171c !important;
            border-collapse: collapse !important;
            width: 100%;
        }
        th {
            background-color: #1f2430 !important;
            color: #e1e1e1 !important;
            font-weight: 600 !important;
            text-transform: uppercase;
        }
        td {
            background-color: #171a21 !important;
            color: #d7d7d7 !important;
            font-size: 0.95rem !important;
            border-top: 1px solid #252a34 !important;
        }
        tr:hover td {
            background-color: #1e2230 !important;
        }
        .pending-title {
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            color: #ffd95e !important;
            margin-bottom: 8px !important;
        }
        .placeholder-box {
            background: #1E1E1E;
            border-radius: 12px;
            padding: 80px;
            text-align: center;
            font-size: 1.2rem;
            color: #bbb;
            box-shadow: 0 0 10px rgba(108, 99, 255, 0.1);
        }
        .main-card {
            border: 1px solid rgba(108, 99, 255, 0.15);
            border-radius: 16px;
        }
    </style>
""", unsafe_allow_html=True)


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

    # ==========================================================
    # 🧮 AUTO-COMPUTE TRAINING WEEK (Start Date → fallback to manual Week)
    # ==========================================================
    if "Start Date" in df.columns:
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce", format="%m/%d/%Y")

        today = pd.Timestamp.now(tz="US/Eastern").normalize()
        df["Auto_Week"] = ((today - df["Start Date"]).dt.days // 7).clip(lower=0)

        if "Week" in df.columns:
            df["Week"] = df["Auto_Week"].where(df["Start Date"].notna(), df["Week"])
        else:
            df["Week"] = df["Auto_Week"]

    df["Week"] = pd.to_numeric(df["Week"], errors="coerce").fillna(0)

    if "Salary" in df.columns:
        df["Salary"] = (
            df["Salary"]
            .astype(str)
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

# ---- CHART ----
st.markdown("---")
left_col, right_col = st.columns([1, 1])
color_map = {
    "Ready for Placement": "#2E91E5",
    "In Training": "#E15F99",
    "Offer Pending": "#A020F0",
}
chart_data = pd.DataFrame({
    "Category": ["Ready for Placement", "In Training", "Offer Pending"],
    "Count": [ready, in_training, offer_pending]
})

with right_col:
    st.subheader("📊 Candidate Status Overview")
    fig_pie = px.pie(
        chart_data, names="Category", values="Count", hole=0.45,
        color="Category", color_discrete_map=color_map
    )
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)", 
        font_color="white", 
        height=400,
        legend=dict(
            font=dict(color="red", size=14)
        ),
        hoverlabel=dict(
            bgcolor="#1a1d27",
            font_color="white",
            font_size=12
        )
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with left_col:
    st.subheader("📍 Open Job Positions")
    if not jobs_df.empty:
        clean_jobs_df = jobs_df[jobs_df["Job Title"].notna()]
        st.dataframe(clean_jobs_df, use_container_width=True, height=400, hide_index=True)
    else:
        st.markdown('<div class="placeholder-box">No job positions data available</div>', unsafe_allow_html=True)

# ==========================================================
# The rest of your code (Ready for Placement, In Training, Matching, Offer Pending)
# ==========================================================
# (No changes below this point)
