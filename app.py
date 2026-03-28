import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Cricket Dashboard", layout="wide")

# =========================
# CUSTOM UI (DARK THEME)
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: #ffffff;
}
section[data-testid="stSidebar"] {
    background-color: #161a23;
}
[data-testid="stMetric"] {
    background-color: #1f2937;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
}
h1, h2, h3 {
    color: #00d4ff;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.title("🏏 Cricket Player Performance Dashboard")
st.markdown("### 🚀 Analyze • Compare • Discover Insights")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("cricketdata.csv")

    df.rename(columns={
        "Mat": "Matches",
        "Inns": "Innings",
        "NO": "Not_Out",
        "Ave": "Average",
        "BF": "Balls_Faced",
        "SR": "Strike_Rate"
    }, inplace=True)

    df["Country"] = df["Player"].str.extract(r"\((.*?)\)")
    df["Player"] = df["Player"].str.replace(r"\(.*\)", regex=True).str.strip()

    for col in ["Runs", "Average", "Strike_Rate"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(inplace=True)
    return df

df = load_data()

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## 🏏 Cricket Dashboard")
st.sidebar.caption("Filter players")

countries = st.sidebar.multiselect(
    "Select Country",
    sorted(df["Country"].unique()),
    default=sorted(df["Country"].unique())
)

filtered_df = df[df["Country"].isin(countries)]

# =========================
# KPI
# =========================
st.subheader("📊 Key Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Players", len(filtered_df))
col2.metric("Avg Runs", int(filtered_df["Runs"].mean()))
col3.metric("Strike Rate", round(filtered_df["Strike_Rate"].mean(), 2))

st.markdown("---")

# =========================
# PLAYER SEARCH (AUTOCOMPLETE)
# =========================
st.subheader("🔍 Search Player")

player = st.selectbox(
    "Type player name",
    sorted(df["Player"].unique()),
    index=None,
    placeholder="Start typing..."
)

if player:
    pdata = df[df["Player"] == player].iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Runs", int(pdata["Runs"]))
    col2.metric("Average", round(pdata["Average"], 2))
    col3.metric("Strike Rate", round(pdata["Strike_Rate"], 2))

    st.dataframe(df[df["Player"] == player])

st.markdown("---")

# =========================
# PLAYER COMPARISON
# =========================
st.subheader("🆚 Player Comparison")

col1, col2 = st.columns(2)

p1 = col1.selectbox("Player 1", df["Player"].unique())
p2 = col2.selectbox("Player 2", df[df["Player"] != p1]["Player"].unique())

d1 = df[df["Player"] == p1].iloc[0]
d2 = df[df["Player"] == p2].iloc[0]

comp = pd.DataFrame({
    "Metric": ["Runs", "Average", "Strike Rate"],
    p1: [d1["Runs"], d1["Average"], d1["Strike_Rate"]],
    p2: [d2["Runs"], d2["Average"], d2["Strike_Rate"]]
})

st.table(comp)

fig, ax = plt.subplots()
x = range(3)

ax.bar(x, comp[p1], width=0.4, label=p1)
ax.bar([i+0.4 for i in x], comp[p2], width=0.4, label=p2)

ax.set_xticks([i+0.2 for i in x])
ax.set_xticklabels(comp["Metric"])
ax.legend()

st.pyplot(fig)

st.markdown("---")

# =========================
# TOP PLAYERS
# =========================
st.subheader("🏆 Top Players")

top = filtered_df.sort_values("Runs", ascending=False).head(10)

fig1, ax1 = plt.subplots()
ax1.barh(top["Player"], top["Runs"])
ax1.invert_yaxis()
st.pyplot(fig1)

# =========================
# SCATTER
# =========================
st.subheader("⚡ Average vs Strike Rate")

fig2, ax2 = plt.subplots()
sns.scatterplot(x="Average", y="Strike_Rate", hue="Country", data=filtered_df, ax=ax2)
st.pyplot(fig2)

# =========================
# PIE
# =========================
st.subheader("🌍 Country Distribution")

fig3, ax3 = plt.subplots()
counts = filtered_df["Country"].value_counts()
ax3.pie(counts, labels=counts.index, autopct="%1.1f%%")
st.pyplot(fig3)

st.markdown("---")

# =========================
# OUTLIERS
# =========================
st.subheader("🔥 High Performers")

Q1 = filtered_df["Average"].quantile(0.25)
Q3 = filtered_df["Average"].quantile(0.75)
IQR = Q3 - Q1

out = filtered_df[filtered_df["Average"] > Q3 + 1.5*IQR]

st.dataframe(out[["Player","Country","Average","Strike_Rate"]])

# =========================
# DOWNLOAD
# =========================
st.subheader("⬇️ Download Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download CSV",
    csv,
    "cricket_analysis.csv",
    "text/csv"
)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("💼 Developed by Gayathri | Streamlit Project")
