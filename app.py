import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="🏏 Cricket Performance Dashboard",
    layout="wide"
)

# =========================
# TITLE
# =========================
st.title("🏏 Cricket Player Performance Dashboard")
st.markdown("### 📊 Explore insights on player performance across countries")

# =========================
# LOAD & CLEAN DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("cricketdata.csv")

    # Rename columns for clarity
    df.rename(columns={
        "Mat": "Matches",
        "Inns": "Innings",
        "NO": "Not_Out",
        "Ave": "Average",
        "BF": "Balls_Faced",
        "SR": "Strike_Rate"
    }, inplace=True)

    # Extract country from Player column
    df["Country"] = df["Player"].str.extract(r"\((.*?)\)")
    df["Player"] = df["Player"].str.replace(r"\(.*\)", "", regex=True).str.strip()

    # Convert to numeric (safe handling)
    numeric_cols = ["Runs", "Average", "Strike_Rate"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove missing values
    df.dropna(inplace=True)

    return df

df = load_data()

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🔍 Filters")

countries = st.sidebar.multiselect(
    "Select Country",
    options=sorted(df["Country"].unique()),
    default=sorted(df["Country"].unique())
)

players = st.sidebar.multiselect(
    "Select Player",
    options=sorted(df["Player"].unique()),
    default=None
)

# Apply filters
filtered_df = df[df["Country"].isin(countries)]

if players:
    filtered_df = filtered_df[filtered_df["Player"].isin(players)]

# =========================
# DATA PREVIEW
# =========================
if st.checkbox("📂 Show Dataset"):
    st.dataframe(filtered_df)

# =========================
# KPI METRICS
# =========================
st.subheader("📊 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric("👤 Total Players", len(filtered_df))
col2.metric("🏏 Average Runs", int(filtered_df["Runs"].mean()))
col3.metric("⚡ Avg Strike Rate", round(filtered_df["Strike_Rate"].mean(), 2))

st.markdown("---")

# =========================
# TOP PLAYERS BAR CHART
# =========================
st.subheader("🏆 Top 10 Players by Runs")

top_players = filtered_df.sort_values(by="Runs", ascending=False).head(10)

fig1, ax1 = plt.subplots()
ax1.barh(top_players["Player"], top_players["Runs"])
ax1.set_xlabel("Runs")
ax1.set_ylabel("Player")
ax1.invert_yaxis()

st.pyplot(fig1)

# =========================
# SCATTER PLOT
# =========================
st.subheader("⚡ Batting Average vs Strike Rate")

fig2, ax2 = plt.subplots()
sns.scatterplot(
    x="Average",
    y="Strike_Rate",
    hue="Country",
    data=filtered_df,
    ax=ax2
)

st.pyplot(fig2)

# =========================
# PIE CHART
# =========================
st.subheader("🌍 Country Distribution")

country_counts = filtered_df["Country"].value_counts()

fig3, ax3 = plt.subplots()
ax3.pie(
    country_counts,
    labels=country_counts.index,
    autopct="%1.1f%%",
    startangle=90
)

st.pyplot(fig3)

# =========================
# OUTLIER DETECTION
# =========================
st.subheader("🔥 High Performing Outliers")

Q1 = filtered_df["Average"].quantile(0.25)
Q3 = filtered_df["Average"].quantile(0.75)
IQR = Q3 - Q1

upper_bound = Q3 + 1.5 * IQR

outliers = filtered_df[filtered_df["Average"] > upper_bound]

st.write(f"🚀 Found {len(outliers)} high-performing players")

st.dataframe(outliers[["Player", "Country", "Average", "Strike_Rate"]])

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("💼 Developed using Python, Pandas, Seaborn & Streamlit")
