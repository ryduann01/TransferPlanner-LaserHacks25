from flask import Flask, render_template, request, jsonify
import pandas as pd
import re

app = Flask(__name__)

# Load Data
gpa_df = pd.read_csv("Combined_UC_Majors_UTF8.csv")
gpa_df["normalized_major"] = gpa_df["major_name"].apply(lambda x: re.sub(r'[^a-zA-Z0-9]', '', str(x)).lower())
salary_df = pd.read_csv("UCI_Earnings_By_Major_Combined_CLEAN_FIXED.csv", names=["label", "2yr", "5yr", "10yr", "major"], skiprows=1)

# Helpers
def normalize(text):
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()

def parse_gpa_range(gpa_range):
    if pd.isna(gpa_range) or "masked" in str(gpa_range).lower():
        return None
    try:
        low, high = map(float, gpa_range.split(" - "))
        return f"{low:.2f} - {high:.2f}"
    except:
        return None

@app.route('/')
def index():
    # Group majors and show campuses where each is offered
    grouped = (
        gpa_df.groupby("major_name")["campus"]
        .apply(lambda x: ", ".join(sorted(set(x))))
        .reset_index()
        .rename(columns={"campus": "campuses"})
    )
    majors = grouped.to_dict(orient="records")
    return render_template("websiteTemplate.html", majors=majors)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    campuses = [c.strip().upper() for c in data['campuses'].split(",")]
    major = normalize(data['major'])

    # GPA & Admit Rate Search
    gpa_matches = gpa_df[
        (gpa_df["campus"].str.upper().isin(campuses)) &
        (gpa_df["normalized_major"] == major)
    ]

    gpa_results = []
    for _, row in gpa_matches.iterrows():
        gpa_results.append({
            "campus": row["campus"],
            "major": row["major_name"],
            "gpa_range": parse_gpa_range(row["admit_gpa_range"]) or "Not available",
            "admit_rate": row["admit_rate"] if pd.notna(row["admit_rate"]) else "Not available"
        })

    # Salary Search
    salary_info = []
    for _, row in salary_df.iterrows():
        if "Median" not in str(row.get("label", "")):
            continue

        if normalize(row.get("major", "")) != major:
            continue

        salary_info.append({
            "label": "Median",
            "y2": row.get("2yr", "N/A"),
            "y5": row.get("5yr", "N/A"),
            "y10": row.get("10yr", "N/A")
        })

    return jsonify({"gpa": gpa_results, "salary": salary_info})

@app.route('/roi', methods=['POST'])
def roi():
    data = request.json
    user_gpa = float(data.get('gpa', 0))
    roi_majors = []

    uci_gpa = gpa_df[gpa_df["campus"].str.upper() == "UCI"].copy()
    uci_gpa["normalized_major"] = uci_gpa["major_name"].apply(normalize)

    seen = set()
    for _, row in salary_df.iterrows():
        if "Median" not in str(row.get("label", "")):
            continue

        norm_major = normalize(row.get("major", ""))
        if norm_major in seen:
            continue
        seen.add(norm_major)

        try:
            salary_clean = int(str(row.get("5yr", "")).replace("$", "").replace(",", ""))
        except:
            continue

        match = uci_gpa[uci_gpa["normalized_major"] == norm_major]
        if match.empty:
            continue

        for _, m in match.iterrows():
            admit_range = parse_gpa_range(m["admit_gpa_range"])
            if not admit_range:
                continue
            try:
                low, high = map(float, admit_range.split(" - "))
                avg_admit = (low + high) / 2
            except:
                continue

            admit_str = str(m.get("admit_rate", ""))
            try:
                admit_val = float(admit_str.replace("%", "")) / 100
            except:
                admit_val = 0.3

            if user_gpa >= low + 0.05 and salary_clean >= 50000:
                roi_majors.append({
                    "major": m["major_name"],
                    "campus": m["campus"],
                    "gpa_range": admit_range,
                    "salary": row.get("5yr", "")
                })

    # Sort by 5-year salary descending and limit to top 5
    roi_majors.sort(key=lambda x: int(str(x['salary']).replace('$','').replace(',','')), reverse=True)
    roi_majors = roi_majors[:5]

    return jsonify({"high_roi": roi_majors})

if __name__ == '__main__':
    app.run(debug=True)
