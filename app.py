import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="🏏 Cricket Analytics Pro",
    layout="wide"
)

# =========================
# CUSTOM UI (PRO DARK THEME)
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0b0f19;
    color: #ffffff;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

[data-testid="stMetric"] {
    background-color: #1f2937;
    padding: 14px;
    border-radius: 12px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
}

h1, h2, h3 {
    color: #00e5ff;
}

.stDataFrame {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.title("🏏 Cricket Analytics Pro Dashboard")
st.caption("AI-powered cricket performance insights platform")

# =========================
# LOAD DATA (OPTIMIZED)
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
    df["Player"] = df["Player"].str.replace(r"\(.*\)", "", regex=True).str.strip()

    for col in ["Runs", "Average", "Strike_Rate"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(inplace=True)

    # AI Score (precomputed for speed)
    df["Performance_Score"] = (
        df["Runs"] * 0.4 +
        df["Average"] * 0.3 +
        df["Strike_Rate"] * 0.3
    )

    return df

df = load_data()

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🎛 Filters")

country_filter = st.sidebar.multiselect(
    "Country",
    sorted(df["Country"].unique()),
    default=sorted(df["Country"].unique())
)

filtered_df = df[df["Country"].isin(country_filter)]

# =========================
# KPI SECTION
# =========================
st.subheader("📊 Key Performance Indicators")

c1, c2, c3 = st.columns(3)

c1.metric("Players", len(filtered_df))
c2.metric("Avg Runs", int(filtered_df["Runs"].mean()))
c3.metric("Strike Rate", round(filtered_df["Strike_Rate"].mean(), 2))

st.markdown("---")

# =========================
# SEARCH (AUTO COMPLETE)
# =========================
st.subheader("🔍 Player Search")

player = st.selectbox(
    "Search Player",
    sorted(df["Player"].unique()),
    index=None,
    placeholder="Type player name..."
)

if player:
    p = df[df["Player"] == player].iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Runs", int(p["Runs"]))
    col2.metric("Average", round(p["Average"], 2))
    col3.metric("Strike Rate", round(p["Strike_Rate"], 2))

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

fig, ax = plt.subplots()
ax.barh(top["Player"], top["Runs"])
ax.invert_yaxis()
st.pyplot(fig)

st.markdown("---")

# =========================
# ML MODEL (OPTIMIZED - NO REBUILD EACH CLICK)
# =========================
X = df[["Matches", "Average", "Strike_Rate"]]
y = df["Runs"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)

score = model.score(X_test, y_test)

st.subheader("🤖 AI Prediction Engine")

st.write(f"📊 Model Accuracy: {round(score, 2)}")

m = st.number_input("Matches", 1, 500, 50)
a = st.number_input("Average", 0.0, 200.0, 40.0)
s = st.number_input("Strike Rate", 0.0, 300.0, 85.0)

if st.button("Predict Runs"):
    pred = model.predict([[m, a, s]])[0]

    st.success(f"🏏 Predicted Runs: {int(pred)}")

    if pred < 1500:
        st.info("🟢 Emerging Player")
    elif pred < 4000:
        st.warning("🟡 Solid Player")
    else:
        st.error("🔴 Superstar Player")

st.markdown("---")

# =========================
# INSIGHTS ENGINE
# =========================
st.subheader("📊 Auto Insights")

st.success(f"🏆 Top Player: {df.loc[df['Runs'].idxmax()]['Player']}")
st.info(f"📊 Best Average: {round(df['Average'].max(),2)}")
st.info(f"⚡ Best Strike Rate: {round(df['Strike_Rate'].max(),2)}")

st.markdown("---")

# =========================
# OUTLIERS
# =========================
st.subheader("🔥 High Performers")

Q1 = filtered_df["Average"].quantile(0.25)
Q3 = filtered_df["Average"].quantile(0.75)

outliers = filtered_df[filtered_df["Average"] > Q3 + 1.5*(Q3-Q1)]

st.dataframe(outliers[["Player","Country","Average","Strike_Rate"]])

st.markdown("---")

# =========================
# DOWNLOAD FEATURE
# =========================
st.subheader("⬇️ Export Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download CSV",
    csv,
    "cricket_dashboard.csv",
    "text/csv"
)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("💼 Built by Gayathri | AI-Powered Cricket Analytics Dashboard")
