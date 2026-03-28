import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Cricket Analysis", layout="wide")

# =========================
# TITLE
# =========================
st.title("🏏 Cricket Player Performance Analysis")
st.markdown("Analyze player performance across countries, styles, and careers.")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("cricketdata.csv")
    return df

df = load_data()

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🔍 Filters")

countries = st.sidebar.multiselect(
    "Select Country",
    options=df["Country"].unique(),
    default=df["Country"].unique()
)

filtered_df = df[df["Country"].isin(countries)]

# =========================
# SHOW DATA
# =========================
if st.checkbox("Show Dataset"):
    st.dataframe(filtered_df)

# =========================
# KPI METRICS
# =========================
st.subheader("📊 Key Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Players", len(filtered_df))
col2.metric("Average Runs", int(filtered_df["Runs"].mean()))
col3.metric("Avg Strike Rate", round(filtered_df["Strike_Rate"].mean(), 2))

# =========================
# TOP PLAYERS
# =========================
st.subheader("🏆 Top 10 Players by Runs")

top_players = filtered_df.sort_values(by="Runs", ascending=False).head(10)

fig, ax = plt.subplots()
ax.bar(top_players["Player"], top_players["Runs"])
plt.xticks(rotation=45)
st.pyplot(fig)

# =========================
# SCATTER PLOT
# =========================
st.subheader("⚡ Average vs Strike Rate")

fig2, ax2 = plt.subplots()
sns.scatterplot(x="Average", y="Strike_Rate", data=filtered_df, ax=ax2)
st.pyplot(fig2)

# =========================
# COUNTRY DISTRIBUTION
# =========================
st.subheader("🌍 Country Distribution")

country_counts = filtered_df["Country"].value_counts()

fig3, ax3 = plt.subplots()
ax3.pie(country_counts, labels=country_counts.index, autopct="%1.1f%%")
st.pyplot(fig3)

# =========================
# OUTLIERS
# =========================
st.subheader("🔥 Outliers (High Performers)")

Q1 = filtered_df["Average"].quantile(0.25)
Q3 = filtered_df["Average"].quantile(0.75)
IQR = Q3 - Q1

upper = Q3 + 1.5 * IQR

outliers = filtered_df[filtered_df["Average"] > upper]

st.dataframe(outliers[["Player", "Average", "Strike_Rate"]])

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("💼 Developed using Python, Pandas, Seaborn & Streamlit")