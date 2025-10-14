import pandas as pd
import streamlit as st
import plotly.express as px

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="MIT Candidate Training Dashboard - Google Sheets", 
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
        /* Prevent light mode flashing */
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
        /* Force all text elements to light color */
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
            color: #E5E7EB !important; /* ensure light text on dark bg */
            font-size: clamp(12px, 1.2vw, 14px) !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        /* Force label/value color across browsers and themes */
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
        div[data-testid="stMetricValue"] * { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }
        /* Help icon inside metrics */
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
            background: #1E1E1E;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #6C63FF;
        }
    </style>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
@st.cache_data(ttl=300)
def load_data():
    from datetime import datetime, timedelta
    
    # Google Sheets CSV export URL
    google_sheets_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSbD6wUrZEt9kuSQpUT2pw0FMOb7h1y8xeX-hDTeiiZUPjtV0ohK_WcFtCSt_4nuxdtn9zqFS8z8aGw/export?format=csv&gid=0"
    
    data_source = None
    try:
        st.markdown('<div class="status-box">🔄 Loading data from Google Sheets...</div>', unsafe_allow_html=True)
        # Try Google Sheets first
        df = pd.read_csv(google_sheets_url)
        data_source = "Google Sheets"
        st.markdown('<div class="status-box">✅ Successfully loaded from Google Sheets!</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.markdown(f'<div class="status-box">⚠️ Google Sheets error: {e}</div>', unsafe_allow_html=True)
        st.markdown('<div class="status-box">📁 No fallback available - this is a Google Sheets only version</div>', unsafe_allow_html=True)
        return pd.DataFrame(), "Error"
    
    # Remove completely empty rows and header rows
    df = df.dropna(how='all')
    
    # Check if required columns exist
    if 'MIT Name' not in df.columns:
        st.error("❌ Column 'MIT Name' not found in data. Please check the Google Sheet structure.")
        st.write("Available columns:", df.columns.tolist())
        return pd.DataFrame(), "Error"
    
    df = df[df['MIT Name'].notna()]
    df = df[df['MIT Name'] != 'MIT Name']  # Remove duplicate headers
    df = df[df['MIT Name'] != 'New Candidate Name']  # Remove template rows
    
    # Clean column names
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    df = df.rename(columns={'Week ': 'Week'})  # Fix trailing space
    
    # Convert Start date to datetime
    if 'Start date' in df.columns:
        df['Start Date'] = pd.to_datetime(df['Start date'], errors='coerce')
    elif 'Start Date' in df.columns:
        df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
    else:
        st.warning("⚠️ No 'Start date' column found")
        df['Start Date'] = None
    
    # Calculate weeks dynamically from start date to today
    today = pd.Timestamp.now()
    
    def calculate_weeks(row):
        start = row['Start Date']
        if pd.isna(start):
            return None
        if start > today:
            # Future start date
            days_until = (start - today).days
            weeks_until = days_until / 7
            return f"-{int(weeks_until)} weeks from start"
        else:
            # Already started - calculate week number (first 7 days = Week 1)
            days_since = (today - start).days
            week_number = (days_since // 7) + 1
            return int(week_number)
    
    df['Week'] = df.apply(calculate_weeks, axis=1)
    
    # Map vertical codes to full names
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
    
    # Convert salary to numeric
    if 'Salary' in df.columns:
        df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce')
    
    # Map Status to Readiness categories
    def infer_readiness(row):
        status = str(row.get('Status', '')).strip()
        week = row.get('Week', None)
        
        # Exclude "Position Identified" from dashboard
        if status == 'Position Identified':
            return 'Position Identified'  # We'll filter these out
        
        # Offer Pending - special category
        if status == 'Offer Pending':
            return 'Offer Pending'
        
        # Offer Accepted -> Started MIT Training
        if status == 'Offer Accepted':
            return 'Started MIT Training'
        
        # Training status
        if status == 'Training':
            if isinstance(week, int):
                if week >= 6:
                    return 'Ready for Placement'
                elif week >= 1:
                    return 'In Training'
                else:
                    return 'Started MIT Training'
            else:
                return 'Started MIT Training'
        
        # Future start dates
        if isinstance(week, str) and 'from start' in week:
            return 'Starting MIT Training'
        
        # Week-based classification for other statuses
        if isinstance(week, int):
            if week >= 6:
                return 'Ready for Placement'
            elif week >= 1:
                return 'In Training'
            else:
                return 'Started MIT Training'
        
        # Default
        return 'Started MIT Training'
    
    df['Readiness'] = df.apply(infer_readiness, axis=1)
    
    # Filter out "Position Identified" candidates
    df = df[df['Readiness'] != 'Position Identified']
    
    return df, data_source

# Load data
df, data_source = load_data()

if df.empty:
    st.error("❌ Unable to load data. Please check the Google Sheet configuration.")
    st.stop()

# ---- DASHBOARD HEADER ----
st.markdown('<div class="dashboard-title">🎓 MIT Candidate Training Dashboard - Google Sheets Test</div>', unsafe_allow_html=True)

# Show data source status
if data_source == "Google Sheets":
    st.success(f"📊 Data Source: {data_source} | Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
elif data_source == "Error":
    st.error("❌ Error loading data")
else:
    st.info(f"📁 Data Source: {data_source}")

# ---- KEY METRICS ----
total = len(df)

# Buckets per new data structure
ready = (df["Readiness"] == "Ready for Placement").sum()
in_training = (df["Readiness"] == "In Training").sum()  # Weeks 1–5
started_training = (df["Readiness"] == "Started MIT Training").sum()
starting_training = (df["Readiness"] == "Starting MIT Training").sum()
offer_pending = (df["Readiness"] == "Offer Pending").sum()
started_mit_training = int(started_training + starting_training)  # grouped bucket

col1, col2, col3, col4, col5 = st.columns(5)

# Executive-facing order: Total → Ready → In Training → Started
col1.metric(
    "Total Candidates",
    total,
    help="All candidates currently in the MIT program dataset"
)
col2.metric(
    "Ready for Placement",
    ready,
    help="Candidates at Week ≥ 6 who are not already placed"
)
col3.metric(
    "In Training (Weeks 1–5)",
    in_training,
    help="Candidates actively progressing through Weeks 1–5 of training"
)
col4.metric(
    "Started MIT Training",
    started_mit_training,
    help="New Program Starts (Week 0) plus those placed at training sites"
)
col5.metric(
    "Offer Pending",
    offer_pending,
    help="Candidates with pending offers awaiting approval"
)

# ---- VISUAL SECTION ----
st.markdown("---")
left_col, right_col = st.columns([1, 1])

# High-contrast, colorblind-friendly palette
color_map = {
    "Ready for Placement": "#2E91E5",      # blue
    "In Training": "#E15F99",              # magenta
    "Started MIT Training": "#1CA71C",     # green
    "Starting MIT Training": "#FBB13C",    # orange
    "Offer Pending": "#A020F0"             # purple
}

# Right side: pie chart
with right_col:
    st.subheader("📊 Candidate Readiness Mix")
    readiness_counts = df["Readiness"].value_counts().reset_index()
    readiness_counts.columns = ["Readiness", "Count"]

    fig_pie = px.pie(
        readiness_counts,
        names="Readiness",
        values="Count",
        hole=0.45,
        color="Readiness",
        color_discrete_map=color_map
    )
    fig_pie.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font_color="white",
        height=400,
        margin=dict(l=0, r=0, t=30, b=30),
        showlegend=True,
    )
    # Improve readability across devices
    fig_pie.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont=dict(color="#FFFFFF", size=14),
        marker=dict(line=dict(color="#0B0F14", width=2))
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Left side: data info
with left_col:
    st.subheader("📋 Data Information")
    st.write(f"**Total Records:** {len(df)}")
    st.write(f"**Columns:** {len(df.columns)}")
    st.write("**Available Columns:**")
    for col in df.columns:
        st.write(f"- {col}")
    
    # Show sample data
    st.subheader("🔍 Sample Data")
    if 'MIT Name' in df.columns and 'Salary' in df.columns:
        sample_df = df[['MIT Name', 'Salary', 'Week', 'Readiness']].head()
        st.dataframe(sample_df, use_container_width=True)
    else:
        st.write("First 5 rows:")
        st.dataframe(df.head(), use_container_width=True)

# ---- QUICK INSIGHTS ----
st.markdown("<h3>🧠 Quick Insights</h3>", unsafe_allow_html=True)

# Helper to list names by readiness category
def get_names(stage):
    return ", ".join(df.loc[df["Readiness"] == stage, "MIT Name"].dropna().tolist())

ready_names      = get_names("Ready for Placement")
inprog_names     = get_names("In Training")
started_names    = get_names("Started MIT Training")
starting_names   = get_names("Starting MIT Training")
offer_pending_names = get_names("Offer Pending")

st.markdown(f"""
<div class="insights-box">
<ul>
    <li><b>{ready}</b> Ready for Placement (Week ≥ 6):<br><i>{ready_names or '—'}</i></li>
    <li><b>{in_training}</b> In Training (Weeks 1–5):<br><i>{inprog_names or '—'}</i></li>
    <li><b>{started_mit_training}</b> Started MIT Training</li>
    <ul>
        <li><b>{started_training}</b> Currently in Training:<br><i>{started_names or '—'}</i></li>
        <li><b>{starting_training}</b> Starting Soon:<br><i>{starting_names or '—'}</i></li>
    </ul>
    <li><b>{offer_pending}</b> Offer Pending:<br><i>{offer_pending_names or '—'}</i></li>
</ul>
</div>
""", unsafe_allow_html=True)

# ---- FULL DATA TABLE ----
st.markdown("---")
st.markdown("### 📋 Full MIT Roster")

# Create a display dataframe with key columns
available_columns = ['MIT Name', 'Week', 'Start Date', 'Salary', 'Status', 'Readiness']
display_columns = [col for col in available_columns if col in df.columns]

if display_columns:
    display_df = df[display_columns].copy()
    
    # Format salary column for display
    if 'Salary' in display_df.columns:
        display_df['Salary'] = display_df['Salary'].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) else "—"
        )
    
    # Format Start Date
    if 'Start Date' in display_df.columns:
        display_df['Start Date'] = pd.to_datetime(display_df['Start Date']).dt.strftime('%m/%d/%Y')
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.dataframe(df, use_container_width=True, hide_index=True)

st.caption("🔄 LIVE DATA: Loading from Google Sheets | Auto-refreshes every 5 minutes | Weeks calculated dynamically from start date")
