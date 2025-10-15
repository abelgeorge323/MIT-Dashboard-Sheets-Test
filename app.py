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
        :root { color-scheme: dark; }
        body, .stApp { background-color: #0b0e14 !important; color: #f5f5f5 !important; }
        h1, h2, h3, h4, h5, h6, p, span, div { color: #f5f5f5 !important; }
        div[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 700 !important; }
        div[data-testid="stMetricLabel"] { font-size: 1rem !important; color: #bbbbbb !important; }
        .stMetric {
            background: #15181e !important; border-radius: 16px !important;
            padding: 24px !important; box-shadow: 0 0 15px rgba(108,99,255,0.15);
            text-align: center;
        }
        .data-source {
            background-color: #143d33; padding: 12px 18px; border-radius: 10px;
            font-weight: 500; color: #e1e1e1; box-shadow: 0 0 10px rgba(0,0,0,0.3);
        }
        [data-testid="stDataFrame"] {
            border-radius: 12px !important; overflow: hidden !important;
            box-shadow: 0 0 10px rgba(108,99,255,0.15);
        }
        table {
            background-color: #14171c !important; border-collapse: collapse !important; width: 100%;
        }
        th {
            background-color: #1f2430 !important; color: #e1e1e1 !important;
            font-weight: 600 !important; text-transform: uppercase;
        }
        td {
            background-color: #171a21 !important; color: #d7d7d7 !important;
            font-size: 0.95rem !important; border-top: 1px solid #252a34 !important;
        }
        tr:hover td { background-color: #1e2230 !important; }
        .placeholder-box {
            background: #1E1E1E; border-radius: 12px; padding: 80px; text-align: center;
            font-size: 1.2rem; color: #bbb; box-shadow: 0 0 10px rgba(108,99,255,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSbD6wUrZEt9kuSQpUT2pw0FMOb7h1y8xeX-hDTeiiZUPjtV0ohK_WcFtCSt_4nuxdtn9zqFS8z8aGw/pub?gid=1155015355&single=true&output=csv"
    df = pd.read_csv(url, skiprows=4).dropna(how="all")
    df.columns = [c.strip() for c in df.columns]
    if "Start date" in df.columns:
        df = df.rename(columns={"Start date": "Start Date"})
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")

    today = pd.Timestamp.now()
    def calc_weeks(row):
        s = row["Start Date"]
        if pd.isna(s): return None
        if s > today: return f"-{int((s - today).days/7)} weeks from start"
        return int(((today - s).days // 7) + 1)
    df["Week"] = df.apply(calc_weeks, axis=1)
    df["Status"] = df["Status"].astype(str).str.strip().str.lower()
    return df

@st.cache_data(ttl=300)
def load_jobs():
    jobs_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSbD6wUrZEt9kuSQpUT2pw0FMOb7h1y8xeX-hDTeiiZUPjtV0ohK_WcFtCSt_4nuxdtn9zqFS8z8aGw/pub?gid=116813539&single=true&output=csv"
    jobs_df = pd.read_csv(jobs_url, skiprows=5).dropna(how="all")
    jobs_df = jobs_df.loc[:, ~jobs_df.columns.str.contains("^Unnamed")]
    return jobs_df

df = load_data()
jobs_df = load_jobs()

# ---- HEADER ----
st.markdown('<h2>🎓 MIT Candidate Training Dashboard</h2>', unsafe_allow_html=True)
st.markdown(f"<div class='data-source'>📊 Data Source: Google Sheets | Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)

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

in_training = len(df[df["Status"].eq("training") & df["Week"].apply(lambda x: isinstance(x, (int, float)) and x <= 6)])
open_jobs = len(jobs_df) if not jobs_df.empty else 0

cols = st.columns(5)
cols[0].metric("Total Candidates", total_candidates)
cols[1].metric("Open Positions", open_jobs)
cols[2].metric("Ready for Placement", ready)
cols[3].metric("In Training (Weeks 1–5)", in_training)
cols[4].metric("Offer Pending", offer_pending)

# ---- JOBS & PIE CHART ----
st.markdown("---")
l, r = st.columns(2)
color_map = {"Ready for Placement": "#2E91E5", "In Training": "#E15F99", "Offer Pending": "#A020F0"}

chart_data = pd.DataFrame({
    "Category": ["Ready for Placement", "In Training", "Offer Pending"],
    "Count": [ready, in_training, offer_pending]
})

with r:
    st.subheader("📊 Candidate Status Overview")
    fig = px.pie(chart_data, names="Category", values="Count", hole=0.45, color="Category", color_discrete_map=color_map)
    fig.update_layout(paper_bgcolor="#0E1117", plot_bgcolor="#0E1117", font_color="white", height=400)
    st.plotly_chart(fig, use_container_width=True)

with l:
    st.subheader("📍 Open Job Positions")
    st.dataframe(jobs_df, use_container_width=True, height=450, hide_index=True)

# ---- OFFER PENDING ----
offer_pending_df = df[df["Status"].str.lower() == "offer pending"]
if not offer_pending_df.empty:
    st.markdown("---")
    st.subheader("🤝 Offer Pending Candidates")
    display_cols = [c for c in ["MIT Name", "Training Site", "Location", "Level"] if c in offer_pending_df.columns]
    st.dataframe(offer_pending_df[display_cols].fillna("—"), use_container_width=True, hide_index=True)
    st.caption(f"{len(offer_pending_df)} candidates with pending offers – awaiting final approval/acceptance")

# ---- MATCH SCORING SECTION ----
st.markdown("---")
st.markdown("""
<div style="background-color:#12151c;padding:15px 25px;border-radius:10px;line-height:1.6;">
<b>🎯 Candidate–Job Match Score Overview</b><br>
Each candidate is scored across five weighted dimensions (100 pts total):
<ul>
<li><b>Vertical Alignment (40 pts)</b> — +30 for exact vertical match, +10 bonus for Aviation/Amazon experience.</li>
<li><b>Salary Trajectory (25 pts)</b> — +25 for ≥5% raise, +15 for ±5%, −10 for lower pay, 0 if missing.</li>
<li><b>Geographic Fit (20 pts)</b> — +20 same city, +10 same state, +5 different state.</li>
<li><b>Confidence (15 pts)</b> — +15 high, +10 moderate, +5 low.</li>
<li><b>Readiness (10 pts)</b> — full points after week 6; proportional before.</li>
</ul>
</div>
""", unsafe_allow_html=True)


def parse_salary(s):
    if not isinstance(s, str) or s.strip() == "": return None
    nums = [float(x.replace("$", "").replace(",", "").strip()) for x in s.replace("–", "-").split("-") if x.strip().replace("$","").replace(",","").isdigit()]
    if len(nums) == 1: return nums[0]
    elif len(nums) == 2: return sum(nums) / 2
    else: return None

if not df.empty and not jobs_df.empty:
    candidates = df.copy()
    jobs = jobs_df.copy()
    candidates["SalaryNum"] = candidates["Salary"].astype(str).str.replace("[\$,]", "", regex=True).replace("", None).astype(float)
    jobs["SalaryNum"] = jobs["Salary"].apply(parse_salary)

    match_records = []
    for _, c in candidates.iterrows():
        for _, j in jobs.iterrows():
            vert_score = 30 if str(c.get("VERT", "")).strip().lower() == str(j.get("VERT", "")).strip().lower() else 0
            if "amazon" in str(c.get("Training Site", "")).lower() or "avia" in str(c.get("Training Site", "")).lower():
                vert_score += 10

            cand_sal, job_sal = c.get("SalaryNum"), j.get("SalaryNum")
            if pd.notna(cand_sal) and pd.notna(job_sal):
                if job_sal >= cand_sal * 1.05: salary_fit = 25
                elif abs(job_sal - cand_sal) / cand_sal <= 0.05: salary_fit = 15
                elif job_sal < cand_sal * 0.95: salary_fit = -10
                else: salary_fit = 0
            else: salary_fit = 0

            cand_city = str(c.get("Location", "")).lower()
            job_city, job_state = str(j.get("City", "")).lower(), str(j.get("State", "")).lower()
            if job_city in cand_city: geo_fit = 20
            elif job_state in cand_city: geo_fit = 10
            else: geo_fit = 5

            conf = 15 if "high" in str(c.get("Confidence", "")).lower() else 10 if "mod" in str(c.get("Confidence", "")).lower() else 5
            w = c.get("Week")
            readiness = 10 if isinstance(w, (int, float)) and w >= 6 else round((w / 6) * 10, 1) if isinstance(w, (int, float)) else 5

            total = vert_score + salary_fit + geo_fit + conf + readiness
            match_records.append({
                "Candidate": c.get("MIT Name", "Unknown"),
                "Job Account": j.get("Account", ""),
                "City": j.get("City", ""),
                "VERT Match": vert_score,
                "Salary Fit": salary_fit,
                "Geo Fit": geo_fit,
                "Confidence": conf,
                "Readiness": readiness,
                "Total Score": total
            })

    match_df = pd.DataFrame(match_records)
    if not match_df.empty:
        best_match_df = match_df.loc[match_df.groupby("Job Account")["Total Score"].idxmax()].reset_index(drop=True)
        st.subheader("🧩 Best Candidate Match per Job Location")
        st.dataframe(best_match_df, use_container_width=True, hide_index=True, height=(len(best_match_df)*35+50))

        fig = px.bar(best_match_df, x="Job Account", y="Total Score", color="Total Score",
                     color_continuous_scale="Plasma", hover_data=["Candidate", "City"],
                     title="📍 Candidate–Job Fit Score by Location")
        fig.update_layout(paper_bgcolor="#0E1117", plot_bgcolor="#0E1117", font_color="white", height=450)
        st.plotly_chart(fig, use_container_width=True)
