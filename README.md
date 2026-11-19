# PlayScope – Google Play Store Analytics Dashboard
## Project Overview

PlayScope is a premium interactive dashboard developed using Python and Streamlit.
It analyzes Google Play Store applications to understand app installs, estimated revenue, category performance and user review sentiment.

## Technologies Used
- Python
- Streamlit
- Pandas
- Plotly
- CSV datasets
## Main Features
1. Premium dark-themed dashboard.
2. Free vs Paid app comparison.
3. Dual-axis chart for average installs and revenue.
4. Top 3 application categories.
5. Data filtering and preprocessing.
6. IST-based chart visibility restriction.
7. Category performance visualization.
8. User review sentiment analysis.
9. Filtered CSV download.

## Data Filters
- Installs >= 10,000
- Paid app revenue >= $10,000
- Android version > 4.0
- App size > 15 MB
- Content rating = Everyone
- App name length <= 30 characters

## Time Restriction

The main dual-axis chart is available only between:

1:00 PM and 2:00 PM IST.

Outside this period, the chart is hidden.

## Installation

Install Python 3.10 or above.

Create virtual environment:

```bash
python -m venv venv
```

Activate on Git Bash:

```bash
source venv/Scripts/activate
```

Install packages:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

## Dataset Structure

```text
data/
    Play Store Data.csv
    User Reviews.csv
```

## Revenue Calculation

Estimated Revenue = Install Count × App Price

Free apps are retained with zero direct download revenue.

The $10,000 revenue threshold applies to paid apps only.

## Developer

Developed as a Google Play Store Data Analytics project.
