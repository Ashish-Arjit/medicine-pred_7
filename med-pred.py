import pandas as pd

# Load dataset
df = pd.read_csv("demo3.csv")

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

def search_medicine_multiple(symptoms_input, age, gender, pregnancy, feeding, df):
    age_group = classify_age_group(age)
    symptoms = [sym.strip().lower() for sym in symptoms_input.split(",")]
    results = []

    # Ask duration
    duration = input("From when are you suffering this problem? (e.g. 2 days, 1 week): ")
    duration_days = parse_duration(duration)

    if duration_days > 7:
        return (f"⚠️ You are suffering for more than 1 week ({duration}).\n"
                f"➡️ Please consult a doctor for proper medical advice.")

    for symptom in symptoms:
        filtered_df = df[
            df['Symptom'].str.lower().str.contains(symptom, na=False) &
            (df['Age Group'].str.strip() == age_group)
        ]

        if filtered_df.empty:
            results.append(f"No suitable medicine found for '{symptom}' in age group '{age_group}'.")
            continue

        # List medicines
        possible_meds = []
        for meds in filtered_df['Medicine'].unique():
            parts = [m.strip() for m in meds.split('+')]
            possible_meds.extend(parts)
        possible_meds = list(dict.fromkeys(possible_meds))  # deduplicate

        print(f"\nFor '{symptom}', recommended medicines for '{age_group}':")
        for i, med in enumerate(possible_meds, 1):
            print(f"{i}. {med}")

        used_before = input("Have you used any medicine before? (yes/no): ").strip().lower()

        if used_before == "yes":
            chosen = input("Enter medicine numbers separated by commas OR type another medicine name: ").strip()

            if chosen.isdigit() or "," in chosen:
                chosen_indices = [int(x.strip())-1 for x in chosen.split(",") if x.strip().isdigit()]
                chosen_meds = [possible_meds[i].lower() for i in chosen_indices if 0 <= i < len(possible_meds)]
            else:
                # user entered a custom medicine
                custom_med = chosen.lower()
                if df['Medicine'].str.lower().str.contains(custom_med).any():
                    chosen_meds = [custom_med]
                    print(f"✅ {custom_med} is a valid medicine found in dataset.")
                else:
                    chosen_meds = []
                    print(f"⚠️ {custom_med} is not found in dataset. Please verify with doctor.")

            if len(chosen_meds) == len(possible_meds):
                results.append(f"For '{symptom}' (since {duration}):\n"
                               f"⚠️ You already used all recommended medicines.\n"
                               f"➡️ Dosage may need adjustment as per your age. Consult doctor.")
            elif chosen_meds:
                results.append(f"For '{symptom}' (since {duration}):\n"
                               f"✅ You already used: {', '.join(chosen_meds)}")
            else:
                results.append(f"For '{symptom}' (since {duration}):\n"
                               f"⚠️ Invalid medicine entered.\n"
                               f"Recommended: {', '.join(possible_meds)}")

        else:
            best = filtered_df.iloc[0]
            results.append(f"For '{symptom}' (since {duration}):\n"
                           f"Medicine: {best['Medicine']}\nDosage: {best['Dosage']}")

    # Pregnancy/Feeding warnings
    if gender == "female" and age >= 18:
        if pregnancy == "yes":
            results.append("\n⚠️ Note: You mentioned pregnancy.\n"
                           "➡️ Some medicines may not be safe. Please consult a doctor before taking them.")
            if feeding == "yes":
                results.append("\n⚠️ Additional Note: You are feeding a baby.\n"
                               "➡️ Extra caution required with medicines. Doctor advice strongly recommended.")

    return "\n\n".join(results)


# ---------------- RUNNING THE PROGRAM ----------------
# Symptoms
while True:
    symptoms_input = input("Enter your symptoms separated by commas (e.g. Fever, Cough): ").strip()
    if symptoms_input:
        break

# Age
while True:
    try:
        age = int(input("Enter your age: ").strip())
        if age >= 0:
            break
    except ValueError:
        print("⚠️ Please enter a valid number for age.")

# Gender as M/F
while True:
    gender_input = input("Enter your gender (M/F): ").strip().lower()
    if gender_input in ["m", "f"]:
        gender = "male" if gender_input == "m" else "female"
        break
    else:
        print("⚠️ Please enter 'M' for Male or 'F' for Female.")

# Pregnancy + Feeding only if female & adult
pregnancy = "no"
feeding = "no"
if gender == "female" and age >= 18:
    while True:
        pregnancy = input("Are you currently pregnant? (yes/no): ").strip().lower()
        if pregnancy in ["yes", "no"]:
            break
        else:
            print("⚠️ Please answer yes or no.")

    if pregnancy == "yes":
        while True:
            feeding = input("Are you feeding a baby? (yes/no): ").strip().lower()
            if feeding in ["yes", "no"]:
                break
            else:
                print("⚠️ Please answer yes or no.")

# Final execution
output = search_medicine_multiple(symptoms_input, age, gender, pregnancy, feeding, df)
print("\nFinal Result:\n")
print(output)
