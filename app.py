from pathlib import Path
from datetime import datetime, time
from zoneinfo import ZoneInfo
import re

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="PlayScope Analytics",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)
BASE_DIR = Path(__file__).resolve().parent

# ==================================================
# 2. CUSTOM CSS
# ==================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #101827, #17243a);
    color: #F8FAFC;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #1E293B);
    border-right: 1px solid #475569;
}
/* Sidebar text */
[data-testid="stSidebar"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: #F8FAFC !important;
}

/* Sidebar headings */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #38BDF8 !important;
    font-weight: 700 !important;
}

/* Sidebar text inputs */
[data-testid="stSidebar"] input {
    background-color: #334155 !important;
    color: #FFFFFF !important;
    border: 1px solid #64748B !important;
}

/* Sidebar dropdowns */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #334155 !important;
    color: #FFFFFF !important;
    border-color: #64748B !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #FFFFFF !important;
}

/* Dropdown options */
[data-baseweb="popover"],
[data-baseweb="menu"] {
    background-color: #1E293B !important;
}

[data-baseweb="menu"] * {
    color: #FFFFFF !important;
}

/* Main headings */
h1, h2, h3 {
    color: #F8FAFC !important;
}

/* KPI cards */
[data-testid="stMetric"] {
    background: #1E293B;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #334155;
}

[data-testid="stMetricLabel"] {
    color: #CBD5E1 !important;
}

[data-testid="stMetricValue"] {
    color: #38BDF8 !important;
}

/* Buttons */
.stButton > button {
    background-color: #0284C7;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #0369A1;
    color: white;
}

/* Dividers */
hr {
    border-color: #334155;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# 3. HELPER FUNCTIONS
# ==================================================

def parse_installs(value):
    if pd.isna(value):
        return 0

    cleaned = re.sub(r"[^0-9]", "", str(value))

    return int(cleaned) if cleaned else 0


def parse_reviews(value):
    if pd.isna(value):
        return 0

    try:
        return int(float(str(value).replace(",", "")))
    except (ValueError, TypeError):
        return 0


def parse_size(value):
    """
    Converts:
    19M  -> 19 MB
    19MB -> 19 MB
    500K -> 0.49 MB
    1G   -> 1024 MB
    """

    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    if value in ["", "NAN", "VARIES WITH DEVICE"]:
        return None

    match = re.search(r"(\d+\.?\d*)", value)

    if not match:
        return None

    number = float(match.group(1))

    if "KB" in value or value.endswith("K"):
        return number / 1024

    if "GB" in value or value.endswith("G"):
        return number * 1024

    # Google Play dataset commonly uses M instead of MB
    if "MB" in value or value.endswith("M"):
        return number

    return None


def format_number(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    if value >= 1_000:
        return f"{value / 1_000:.1f}K"

    return f"{value:,.0f}"


# ==================================================
# 4. FIND AND LOAD DATASET
# ==================================================

possible_files = [
    BASE_DIR / "data" / "Play Store Data.csv",
    BASE_DIR / "data" / "Play Store Data(1).csv",
    BASE_DIR / "Play Store Data.csv",
    BASE_DIR / "Play Store Data(1).csv"
]

DATA_FILE = next(
    (file for file in possible_files if file.exists()),
    None
)

st.title("📱 PlayScope Analytics")
st.caption("Google Play Store — Application Performance Dashboard")

if DATA_FILE is None:
    st.error(
        "Play Store dataset not found. Place your CSV file in "
        "the data folder or in the same folder as app.py."
    )

    st.code("""
PlayScope/
│
├── app.py
├── requirements.txt
│
└── data/
    └── Play Store Data.csv
""")

    st.stop()


try:
    original_df = pd.read_csv(DATA_FILE)
except Exception as error:
    st.error(f"Error reading CSV file: {error}")
    st.stop()


# ==================================================
# 5. CHECK DATASET COLUMNS
# ==================================================

required_columns = [
    "App",
    "Category",
    "Rating",
    "Reviews",
    "Size",
    "Installs",
    "Last Updated"
]

missing_columns = [
    column for column in required_columns
    if column not in original_df.columns
]

if missing_columns:
    st.error(
        "Missing columns in CSV: "
        + ", ".join(missing_columns)
    )
    st.stop()

if original_df.empty:
    st.error("The CSV file contains no application records.")
    st.stop()


# ==================================================
# 6. DATA CLEANING
# ==================================================

df = original_df.copy()

# Convert columns
df["Rating"] = pd.to_numeric(
    df["Rating"],
    errors="coerce"
)

df["Reviews_Num"] = df["Reviews"].apply(
    parse_reviews
)

df["Installs_Num"] = df["Installs"].apply(
    parse_installs
)

df["Size_MB"] = df["Size"].apply(
    parse_size
)

df["Last Updated"] = pd.to_datetime(
    df["Last Updated"],
    errors="coerce"
)

df["Category"] = df["Category"].astype(str).str.strip()

df["App"] = df["App"].astype(str).str.strip()

df["Updated_Month"] = df["Last Updated"].dt.month


# ==================================================
# 7. SIDEBAR
# ==================================================

with st.sidebar:

    st.title("🎛️ Dashboard Controls")

    st.markdown("---")

    st.subheader("📌 Active Filters")

    st.markdown("""
    **Minimum Rating:** 4.0

    **Minimum App Size:** 10 MB

    **Last Updated:** January

    **Category Ranking:** Top 10 by installs

    **Chart Time:** 1 PM – 2 PM IST
    """)

    st.markdown("---")

    st.subheader("🔎 Search Applications")

    search_app = st.text_input(
        "Search by application name",
        placeholder="Enter app name..."
    )

    st.markdown("---")

    st.subheader("📊 Dataset Information")

    st.write(f"Dataset: {DATA_FILE.name}")

    st.write(f"Raw records: {len(original_df):,}")

    st.markdown("---")

    st.caption("PlayScope Analytics | 2026")


# ==================================================
# 8. APPLY FILTERS
# ==================================================

# Keep total application count based on the original dataset.
total_apps = len(original_df)

# Apply required filters.
filtered_df = df[
    (df["Rating"] >= 4.0) &
    (df["Size_MB"] >= 10) &
    (df["Updated_Month"] == 1)
].copy()

# Optional search
if search_app:
    filtered_df = filtered_df[
        filtered_df["App"].str.contains(
            search_app,
            case=False,
            na=False
        )
    ]


# ==================================================
# 9. KPI SECTION
# ==================================================

qualified_apps = len(filtered_df)

qualified_categories = filtered_df["Category"].nunique()

total_installs = filtered_df["Installs_Num"].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "TOTAL APPLICATIONS",
        format_number(total_apps)
    )

with col2:
    st.metric(
        "QUALIFIED APPLICATIONS",
        format_number(qualified_apps)
    )

with col3:
    st.metric(
        "QUALIFIED CATEGORIES",
        format_number(qualified_categories)
    )

with col4:
    st.metric(
        "TOTAL INSTALLS",
        format_number(total_installs)
    )


st.markdown("---")


# ==================================================
# 10. CATEGORY PERFORMANCE CHART
#     VISIBLE ONLY 1 PM TO 2 PM IST
# ==================================================

st.subheader("📈 Category Performance Analysis")

st.write(
    "Average app rating and total reviews for the "
    "top 10 categories ranked by installs."
)


@st.fragment(run_every="30s")
def display_category_chart():

    now = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    current_time = now.time()

    # 1 PM inclusive, 2 PM exclusive
    start_time = time(13, 0)
    end_time = time(14, 0)

    if start_time <= current_time < end_time:

        if filtered_df.empty:
            st.warning(
                "No applications match all the selected filters. "
                "Check the data and filter summary below."
            )
            return

        category_summary = (
            filtered_df
            .groupby("Category")
            .agg(
                Average_Rating=("Rating", "mean"),
                Total_Reviews=("Reviews_Num", "sum"),
                Total_Installs=("Installs_Num", "sum"),
                App_Count=("App", "count")
            )
            .reset_index()
        )

        category_summary = category_summary[
            category_summary["Average_Rating"] >= 4.0
        ]

        top_categories = (
            category_summary
            .sort_values(
                "Total_Installs",
                ascending=False
            )
            .head(10)
        )

        if top_categories.empty:
            st.warning("No categories available for the chart.")
            return

        fig = make_subplots(
            specs=[[{"secondary_y": True}]]
        )

        # Average rating
        fig.add_trace(
            go.Bar(
                x=top_categories["Category"],
                y=top_categories["Average_Rating"],
                name="Average Rating",
                marker_color="#38BDF8",
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Average Rating: %{y:.2f}"
                    "<extra></extra>"
                )
            ),
            secondary_y=False
        )

        # Total reviews
        fig.add_trace(
            go.Bar(
                x=top_categories["Category"],
                y=top_categories["Total_Reviews"],
                name="Total Reviews",
                marker_color="#A78BFA",
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Total Reviews: %{y:,.0f}"
                    "<extra></extra>"
                )
            ),
            secondary_y=True
        )

        fig.update_layout(
            title="Top 10 Categories: Average Rating vs Total Reviews",
            barmode="group",
            height=560,
            template="plotly_dark",
            paper_bgcolor="#17243A",
            plot_bgcolor="#17243A",
            font=dict(
                color="#F8FAFC",
                size=12
            ),
            legend=dict(
                orientation="h",
                y=1.12,
                x=0
            ),
            margin=dict(
                l=60,
                r=60,
                t=100,
                b=100
            )
        )

        fig.update_xaxes(
            title_text="Application Categories",
            tickangle=-35,
            showgrid=False
        )

        fig.update_yaxes(
            title_text="Average Rating",
            range=[0, 5],
            secondary_y=False,
            gridcolor="#334155"
        )

        fig.update_yaxes(
            title_text="Total Reviews",
            secondary_y=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.success(
            "Chart is active. It is available until 2:00 PM IST."
        )

        st.caption(
            "Last checked: "
            + now.strftime("%I:%M:%S %p IST")
        )

        with st.expander("View chart data"):

            st.dataframe(
                top_categories,
                use_container_width=True,
                hide_index=True
            )

    else:

        st.info(
            "⏰ This chart is available only between "
            "**1:00 PM and 2:00 PM IST**."
        )

        st.write(
            "The chart will appear automatically during "
            "the permitted time window."
        )

        st.caption(
            "Current time: "
            + now.strftime("%I:%M:%S %p IST")
        )


display_category_chart()


# ==================================================
# 11. FILTER DIAGNOSTICS
# ==================================================

with st.expander("🔧 Check data and filter results"):

    st.write(f"Original CSV records: {len(original_df):,}")

    st.write(
        "Records with valid ratings:",
        int(df["Rating"].notna().sum())
    )

    st.write(
        "Records with recognized app sizes:",
        int(df["Size_MB"].notna().sum())
    )

    st.write(
        "Records with valid update dates:",
        int(df["Last Updated"].notna().sum())
    )

    st.write(
        "Records updated in January:",
        int((df["Updated_Month"] == 1).sum())
    )

    st.write(
        "Records passing all filters:",
        len(filtered_df)
    )

    st.write("Loaded file:", str(DATA_FILE))


# ==================================================
# 12. CATEGORY SUMMARY
# ==================================================

st.markdown("---")

st.subheader("📂 Application Category Summary")

if not filtered_df.empty:

    category_counts = (
        filtered_df
        .groupby("Category")
        .agg(
            Applications=("App", "count"),
            Average_Rating=("Rating", "mean"),
            Total_Installs=("Installs_Num", "sum")
        )
        .reset_index()
        .sort_values(
            "Total_Installs",
            ascending=False
        )
    )

    category_counts["Average_Rating"] = (
        category_counts["Average_Rating"].round(2)
    )

    st.bar_chart(
        category_counts.set_index("Category")["Applications"],
        color="#38BDF8"
    )

    st.dataframe(
        category_counts,
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning(
        "No applications currently match the filters."
    )


# ==================================================
# 13. APPLICATION DATABASE
# ==================================================

st.markdown("---")

st.subheader("🗂️ Application Database")

display_columns = [
    "App",
    "Category",
    "Rating",
    "Reviews_Num",
    "Size_MB",
    "Installs_Num",
    "Last Updated"
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True
)

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv_data,
    file_name="playscope_filtered_data.csv",
    mime="text/csv"
)


# ==================================================
# 14. FOOTER
# ==================================================

st.markdown("---")

st.caption(
    "© 2026 PlayScope Analytics | "
    "Google Play Store Data Analysis Dashboard"
)
