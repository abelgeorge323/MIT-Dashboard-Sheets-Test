# --------------------------------------------------
# MIT Candidate Training Dashboard - Full App
# --------------------------------------------------
import streamlit as st
import pandas as pd
import re
import plotly.express as px
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="MIT Candidate Training Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("## 🧭 MIT Candidate Training Dashboard")
st.markdown(f"**Data Source:** Google Sheets | **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# --------------------------------------------------
# LOAD DATA (replace with your live sources)
# --------------------------------------------------
# Example: Replace with your existing code that loads from Google Sheets
candidates = pd.DataFrame({
    "Name": ["Kathryn Keillor", "RaiDion Fails", "Evan Tichenor", "Micah Scherrei", "Ives Mullen", "Shaquille Thomas"],
    "Vertical": ["TECH", "MANU", "TECH", "MANU", "FIN", "MANU"],
    "City": ["Rochester", "San Francisco", "Elk Grove", "Salt Lake City", "San Francisco", "Salt Lake City"],
    "State": ["NY", "CA", "IL", "UT", "CA", "UT"],
    "Salary": [68000, 72000, 69000, 71000, 75000, 74000],
    "Confidence": ["High", "Moderate", "High", "Moderate", "High", "Low"],
    "Week": [6, 5, 4, 6, 2, 3]
})

open_jobs = pd.DataFrame({
    "Title": ["Data Engineer", "Project Manager", "Software Engineer", "QA Analyst", "Business Analyst", "Cloud Engineer"],
    "Account": ["Geico", "Mars", "Oracle", "Quidel Ortho", "Collins Aerospace", "Wells Fargo"],
    "VERT": ["TECH", "MANU", "TECH", "HEA", "AER", "FIN"],
    "City": ["Indianapolis", "Salt Lake City", "Elk Grove", "Rochester", "Rockford", "San Francisco"],
    "State": ["IN", "UT", "IL", "NY", "IL", "CA"],
    "Salary": ["$70,000–$75,000", "$72,000–$78,000", "$71,000–$74,000", "$68,000–$70,000", "$69,000–$73,000", "$75,000–$80,000"]
})

# --------------------------------------------------
# METRICS ROW
# --------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🧑‍🎓 Total Candidates", len(candidates))
col2.metric("📍 Open Positions", len(open_jobs))
col3.metric("🚀 Ready for Placement", sum(candidates["Week"] >= 6))
col4.metric("📘 In Training (Weeks 1–5)", sum((candidates["Week"] > 0) & (candidates["Week"] < 6)))
col5.metric("📄 Offer Pending", 4)

# --------------------------------------------------
# OPEN JOB POSITIONS
# --------------------------------------------------
st.markdown("### 📋 Open Job Positions")
open_jobs_display = open_jobs[["Title", "Account", "City", "State", "Salary", "VERT"]]
st.dataframe(open_jobs_display, use_container_width=True)

# --------------------------------------------------
# CANDIDATE STATUS OVERVIEW (Pie Chart)
# --------------------------------------------------
status_summary = {
    "In Training": sum((candidates["Week"] > 0) & (candidates["Week"] < 6)),
    "Ready for Placement": sum(candidates["Week"] >= 6),
    "Offer Pending": 4
}
fig_status = px.pie(
    names=list(status_summary.keys()),
    values=list(status_summary.values()),
    color_discrete_sequence=px.colors.sequential.Purples,
    title="Candidate Status Overview"
)
st.plotly_chart(fig_status, use_container_width=True)

# --------------------------------------------------
# OFFER PENDING CANDIDATES
# --------------------------------------------------
st.markdown("### 📝 Offer Pending Candidates")
offer_pending = pd.DataFrame({
    "Name": ["Kathryn Keillor", "RaiDion Fails", "Micah Scherrei", "Shaquille Thomas"],
    "Training Site": ["Quidel Ortho", "Mars", "Ford", "Collins"],
    "Location": ["Durango, CO", "San Jose, CA", "Detroit, MI", "St. Louis, MO"],
    "Level": ["ADM", "QM", "TM", "ADM"]
})
st.dataframe(offer_pending, use_container_width=True)

# --------------------------------------------------
# 🧮 CANDIDATE–JOB MATCH SCORE SECTION
# --------------------------------------------------
st.markdown("### 🎯 Candidate–Job Match Score Overview")
st.markdown("""
Each candidate is scored across five weighted dimensions (100 pts total):

- **Vertical Alignment (40 pts)** → +30 for exact vertical match, +10 bonus for Amazon/Aviation experience  
- **Salary Trajectory (25 pts)** → +25 for ≥5% raise, +15 for ±5%, −10 for lower pay, 0 if missing  
- **Geographic Fit (20 pts)** → +20 same city, +10 same state, +5 different state  
- **Confidence (15 pts)** → +15 high, +10 moderate, +5 low  
- **Readiness (10 pts)** → full points after week 6; proportional before  
""")

# --- Clean Salary Field ---
def clean_salary(value):
    """Convert salary ranges like '$70,000–$75,000' to numeric midpoint, else return None."""
    if isinstance(value, str):
        nums = re.findall(r'\d+', value.replace(',', ''))
        if len(nums) >= 2:
            return (float(nums[0]) + float(nums[1])) / 2
        elif len(nums) == 1:
            return float(nums[0])
    return None

open_jobs["SalaryNum"] = open_jobs["Salary"].apply(clean_salary)

# --- Matching Function ---
def calculate_match_scores(candidates_df, jobs_df):
    matches = []

    for _, cand in candidates_df.iterrows():
        for _, job in jobs_df.iterrows():
            # 1️⃣ Vertical Alignment
            vert_score = 0
            if cand["Vertical"] == job["VERT"]:
                vert_score += 30
            if cand["Vertical"] in ["AMZ", "AVI"]:
                vert_score += 10

            # 2️⃣ Salary Trajectory
            sal_score = 0
            cand_sal = cand.get("Salary", None)
            job_sal = job.get("SalaryNum", None)
            if isinstance(cand_sal, (int, float)) and isinstance(job_sal, (int, float)):
                diff = (job_sal - cand_sal) / cand_sal
                if diff >= 0.05:
                    sal_score = 25
                elif abs(diff) <= 0.05:
                    sal_score = 15
                elif diff < -0.05:
                    sal_score = -10
            # else 0 if no salary

            # 3️⃣ Geographic Fit
            geo_score = 5
            if cand["City"] == job["City"]:
                geo_score = 20
            elif cand["State"] == job["State"]:
                geo_score = 10

            # 4️⃣ Confidence Level
            conf_map = {"High": 15, "Moderate": 10, "Low": 5}
            conf_score = conf_map.get(cand.get("Confidence", "Low"), 5)

            # 5️⃣ Readiness
            week = cand.get("Week", 0)
            ready_score = 10 if week >= 6 else max(1.5 * week, 0)

            total = vert_score + sal_score + geo_score + conf_score + ready_score

            matches.append({
                "Candidate": cand["Name"],
                "Job Account": job["Account"],
                "City": job["City"],
                "VERT Match": vert_score,
                "Salary Fit": sal_score,
                "Geo Fit": geo_score,
                "Confidence": conf_score,
                "Readiness": round(ready_score, 1),
                "Total Score": round(total, 1)
            })

    return pd.DataFrame(matches)

# --- Generate Matches ---
match_df = calculate_match_scores(candidates, open_jobs)

# --- Display the Match Table ---
st.dataframe(
    match_df.style.format({
        "VERT Match": "{:.0f}",
        "Salary Fit": "{:.0f}",
        "Geo Fit": "{:.0f}",
        "Confidence": "{:.0f}",
        "Readiness": "{:.1f}",
        "Total Score": "{:.1f}"
    }),
    use_container_width=True
)

# --- Top 10 Chart ---
st.markdown("### 📊 Top Candidate–Job Matches")
top_matches = match_df.sort_values("Total Score", ascending=False).head(10)
fig_top = px.bar(
    top_matches,
    x="Candidate",
    y="Total Score",
    color="Job Account",
    text="Total Score",
    color_discrete_sequence=px.colors.sequential.Purples,
    title="Top 10 Candidate–Job Matches"
)
st.plotly_chart(fig_top, use_container_width=True)

# --------------------------------------------------
# END
# --------------------------------------------------
st.markdown("###### © 2025 MIT Candidate Dashboard | Internal Use Only")
