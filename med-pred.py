from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import pandas as pd

# Load dataset
df = pd.read_csv("demo3.csv")

app = FastAPI(title="Medicine Recommendation API")

def classify_age_group(age):
    if age < 1:
        return "Below 1 year"
    elif 1 <= age <= 3:
        return "1-3 years"
    elif 4 <= age <= 6:
        return "3-6 years"
    elif 7 <= age <= 15:
        return "6-15 years"
    else:
        return "Above 15 years"

def parse_duration(duration_str):
    duration_str = duration_str.lower().strip()
    days = 0
    if "day" in duration_str:
        try:
            days = int(duration_str.split()[0])
        except:
            days = 0
    elif "week" in duration_str:
        try:
            weeks = int(duration_str.split()[0])
            days = weeks * 7
        except:
            days = 7
    return days

@app.get("/recommend")
def search_medicine_multiple(
    symptoms: str = Query(..., description="Comma-separated symptoms"),
    age: int = Query(..., ge=0, description="Age of the patient"),
    gender: str = Query(..., regex="^(male|female)$", description="Gender: male/female"),
    pregnancy: str = Query("no", regex="^(yes|no)$", description="Pregnancy status"),
    feeding: str = Query("no", regex="^(yes|no)$", description="Feeding a baby"),
    duration: str = Query("2 days", description="How long suffering (e.g. '2 days', '1 week')")
):
    age_group = classify_age_group(age)
    symptoms_list = [sym.strip().lower() for sym in symptoms.split(",")]
    duration_days = parse_duration(duration)
    results = []

    if duration_days > 7:
        return JSONResponse(content={
            "warning": f"You are suffering for more than 1 week ({duration}). Please consult a doctor."
        })

    for symptom in symptoms_list:
        filtered_df = df[
            df['Symptom'].str.lower().str.contains(symptom, na=False) &
            (df['Age Group'].str.strip() == age_group)
        ]

        if filtered_df.empty:
            results.append({
                "symptom": symptom,
                "message": f"No suitable medicine found for '{symptom}' in age group '{age_group}'."
            })
            continue

        best = filtered_df.iloc[0]
        results.append({
            "symptom": symptom,
            "medicine": best["Medicine"],
            "dosage": best["Dosage"],
            "age_group": age_group,
            "duration": duration
        })

    if gender == "female" and age >= 18:
        if pregnancy == "yes":
            results.append({
                "note": "Pregnancy detected. Some medicines may not be safe. Please consult a doctor."
            })
            if feeding == "yes":
                results.append({
                    "note": "You are feeding a baby. Extra caution required with medicines."
                })

    return {"results": results}
