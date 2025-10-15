import pandas as pd
import streamlit as st
import plotly.express as px

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="MIT Candidate Training Dashboard", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- CUSTOM STYLING ----
st.markdown("""
    <style>
        /* Force dark mode globally */
        :root {
            color-scheme: dark;
        }
        html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
            background-color: #0E1117 !important;
            color: #FAFAFA !important;
        }
        * {
            color-scheme: dark !important;
        }
        [data-testid="stAppViewContainer"] {
            background-color: #0E1117;
            color: white;
        }
        section[data-testid="stSidebar"] {
            background-color: #1E1E1E !important;
        }
        p, span, div, label, h1, h2, h3, h4, h5, h6 {
            color: #FAFAFA !important;
        }
        .dashboard-title {
            font-size: clamp(1.6rem, 3.2vw, 2.3rem);
            font-weight: 700;
            color: white;
            background: linear-gradient(90deg, #6C63FF, #00B4DB);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        div[data-testid="stMetric"] {
            background: #1E1E1E;
            border-radius: 15px;
            padding: 20px 25px;
            box-shadow: 0 0 12px rgba(108, 99, 255, 0.25);
            border-left: 6px solid #6C63FF;
            transition: 0.3s ease;
            min-width: 220px;
        }
        div[data-testid="stMetric"]:hover {
            box-shadow: 0 0 25px rgba(108, 99, 255, 0.5);
            transform: scale(1.03);
        }
        div[data-testid="stMetricValue"] {
            color: white !important;
            font-size: clamp(22px, 2.2vw, 30px) !important;
            font-weight: bold !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #E5E7EB !important;
            font-size: clamp(12px, 1.2vw, 14px) !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] *,
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            color: #F3F4F6 !important;
            -webkit-text-fill-color: #F3F4F6 !important;
            mix-blend-mode: normal !important;
            opacity: 1 !important;
        }
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * { 
            color: #FFFFFF !important; 
            -webkit-text-fill-color: #FFFFFF !important; 
        }
        div[data-testid="stMetric"] svg path { fill: #E5E7EB !important; }
        @media (max-width: 1400px) {
            div[data-testid="stMetric"] { min-width: 200px; padding: 18px 20px; }
        }
        @media (max-width: 1100px) {
            div[data-testid="stMetric"] { min-width: 170px; padding: 16px 18px; }
        }
        h3, h4 {
            color: white !important;
            font-weight: 600;
        }
        .insights-box {
            background: #1E1E1E;
            border-radius: 12px;
            padding: 20px;
            margin-top: 15px;
            box-shadow: 0 0 10px rgba(108, 99, 255, 0.15);
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
        .status-box {
            display: none !important; /* Hide all loading boxes */
        }
    </style>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
@st.cache_data(ttl=300)
def load_data():
    main_data_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSbD6wUrZEt9kuSQpUT2pw0FMOb7h1y8xeX-hDTeiiZUPjtV0ohK_WcFtCSt_4nuxdtn9zqFS8z8aGw/pub?gid=1155015355&single=true&output=csv"
    data_source = None

    try:
        df = pd.read_csv(main_data_url, skiprows=4)
        data_source = "Google Sheets"
    except Exception as e:
        st.error(f"⚠️ Google Sheets error: {e}")
        return pd.DataFrame(), "Error"

    df = df.dropna(how='all')
    if 'MIT Name' not in df.columns:
        st.error("❌ Column 'MIT Name' not found.")
        return pd.DataFrame(), "Error"

    df = df[df['MIT Name'].notna()]
    df = df[df['MIT Name'] != 'MIT Name']
    df = df[df['MIT Name'] != 'New Candidate Name']
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    df = df.rename(columns={'Week ': 'Week'})

    if 'Start date' in df.columns:
        df['Start Date'] = pd.to_datetime(df['Start date'], errors='coerce')
    elif 'Start Date' in df.columns:
        df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
    else:
        df['Start Date'] = None

    today = pd.Timestamp.now()

    def calculate_weeks(row):
        start = row['Start Date']
        if pd.isna(start):
            return None
        if start > today:
            return f"-{int((start - today).days / 7)} weeks from start"
        return int(((today - start).days // 7) + 1)

    df['Week'] = df.apply(calculate_weeks, axis=1)

    vertical_map = {
        'MANU': 'Manufacturing',
        'AUTO': 'Automotive',
        'FIN': 'Finance',
        'TECH': 'Technology',
        'AVI': 'Aviation',
        'DIST': 'Distribution',
        'RD': 'R&D',
        'Reg & Div': 'Regulatory & Division'
    }
    if 'VERT' in df.columns:
        df['Vertical Full'] = df['VERT'].map(vertical_map).fillna(df['VERT'])

    if 'Salary' in df.columns:
        df['Salary'] = df['Salary'].astype(str).str.replace('$', '').str.replace(',', '').str.replace(' ', '')
        df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce')

    def infer_readiness(row):
        status = str(row.get('Status', '')).strip()
        week = row.get('Week', None)
        if status == 'Position Identified':
            return 'Position Identified'
        if status == 'Offer Pending':
            return 'Offer Pending'
        if status == 'Offer Accepted':
            return 'Started MIT Training'
        if status == 'Training':
            if isinstance(week, int):
                return 'Ready for Placement' if week >= 6 else 'In Training'
            return 'Started MIT Training'
        if isinstance(week, str) and 'from start' in week:
            return 'Starting MIT Training'
        if isinstance(week, int):
            return 'Ready for Placement' if week >= 6 else 'In Training'
        return 'Started MIT Training'

    df['Readiness'] = df.apply(infer_readiness, axis=1)
    df = df[df['Readiness'] != 'Position Identified']

    return df, data_source


@st.cache_data(ttl=300)
def load_jobs_data():
    jobs_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSbD6wUrZEt9kuSQpUT2pw0FMOb7h1y8xeX-hDTeiiZUPjtV0ohK_WcFtCSt_4nuxdtn9zqFS8z8aGw/pub?gid=116813539&single=true&output=csv"
    try:
        jobs_df = pd.read_csv(jobs_url, skiprows=5, header=0)

# Remove any unnamed index columns automatically
        jobs_df = jobs_df.loc[:, ~jobs_df.columns.str.contains('^Unnamed')]
        if 'JV Link' in jobs_df.columns:
            jobs_df = jobs_df.drop('JV Link', axis=1)
        if 'JV ID' in jobs_df.columns:
            jobs_df = jobs_df.drop('JV ID', axis=1)
        jobs_df = jobs_df.dropna(how='all')
        if 'Job Title' in jobs_df.columns:
            jobs_df = jobs_df.dropna(subset=['Job Title'])
            jobs_df = jobs_df[jobs_df['Job Title'].str.strip() != '']
        jobs_df = jobs_df.fillna('')
        return jobs_df
    except Exception as e:
        st.error(f"Error loading jobs data: {e}")
        return pd.DataFrame()


# ---- LOAD ----
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
total = len(df)
ready = (df["Readiness"] == "Ready for Placement").sum()
in_training = (df["Readiness"] == "In Training").sum()
started_training = (df["Readiness"] == "Started MIT Training").sum()
starting_training = (df["Readiness"] == "Starting MIT Training").sum()
offer_pending = (df["Readiness"] == "Offer Pending").sum()
started_mit_training = int(started_training + starting_training)
open_jobs = len(jobs_df) if not jobs_df.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Candidates", total)
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
    "Started MIT Training": "#1CA71C",
    "Starting MIT Training": "#FBB13C",
    "Offer Pending": "#A020F0"
}
with right_col:
    st.subheader("📊 Candidate Readiness Mix")
    readiness_counts = df["Readiness"].value_counts().reset_index()
    readiness_counts.columns = ["Readiness", "Count"]
    fig_pie = px.pie(readiness_counts, names="Readiness", values="Count", hole=0.45,
                     color="Readiness", color_discrete_map=color_map)
    fig_pie.update_layout(paper_bgcolor="#0E1117", plot_bgcolor="#0E1117", font_color="white", height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

with left_col:
    st.subheader("📍 Open Job Positions")
    if not jobs_df.empty:
        st.dataframe(jobs_df, use_container_width=True, height=450, hide_index=True)
    else:
        st.markdown('<div class="placeholder-box">No job positions data available</div>', unsafe_allow_html=True)
