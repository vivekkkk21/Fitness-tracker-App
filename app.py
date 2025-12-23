import streamlit as st
import json
import os
from datetime import datetime

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Workout Planner",
    layout="centered"
)

WORKOUT_FILE = "workouts.json"
PROGRESS_FILE = "progress.json"

# -------------------------------------------------
# UTILS
# -------------------------------------------------
def load_json(path, default):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f, indent=4)
        return default

    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        st.error(f"Invalid JSON detected in {path}. Fix formatting.")
        return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
workouts = load_json(WORKOUT_FILE, {})
progress = load_json(PROGRESS_FILE, {})

today = datetime.now().strftime("%A")

if today not in progress:
    progress[today] = {}

# -------------------------------------------------
# STYLES
# -------------------------------------------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
}

.header {
    font-size: 28px;
    font-weight: 700;
}

.sub {
    font-size: 14px;
    color: #9ca3af;
    margin-bottom: 20px;
}

.exercise-card {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    transition: all 0.2s ease;
}

.exercise-card.completed {
    background-color: #064e3b;
    border-color: #10b981;
}

.exercise-name {
    font-size: 15px;
    font-weight: 500;
    color: #e5e7eb;
}

.exercise-name.completed {
    text-decoration: line-through;
    opacity: 0.8;
}

.exercise-meta {
    font-size: 13px;
    color: #9ca3af;
}

.exercise-meta.completed {
    color: #d1fae5;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
mode = st.sidebar.radio("Mode", ["Today's Workout", "Edit Workout", "Settings"])

# -------------------------------------------------
# TODAY'S WORKOUT
# -------------------------------------------------
if mode == "Today's Workout":
    st.markdown(f"<div class='header'>{today}</div>", unsafe_allow_html=True)

    if today not in workouts:
        st.warning("No workout defined for today.")
    else:
        workout = workouts[today]
        st.markdown(f"<div class='sub'>{workout['muscle_group']}</div>", unsafe_allow_html=True)

        completed_count = 0
        total = len(workout["exercises"])

        for i, ex in enumerate(workout["exercises"]):
            key = f"{today}_{i}"
            done = progress[today].get(key, False)

            cols = st.columns([0.07, 0.93])
            checked = cols[0].checkbox("", value=done, key=key)

            progress[today][key] = checked
            if checked:
                completed_count += 1

            card_class = "exercise-card completed" if checked else "exercise-card"
            text_class = "completed" if checked else ""

            cols[1].markdown(
                f"""
                <div class="{card_class}">
                    <div class="exercise-name {text_class}">
                        {ex['name']}
                    </div>
                    <div class="exercise-meta {text_class}">
                        {ex['sets']} × {ex['reps']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        save_json(PROGRESS_FILE, progress)
        st.progress(completed_count / total if total else 0)

# -------------------------------------------------
# EDIT WORKOUT
# -------------------------------------------------
elif mode == "Edit Workout":
    st.header("Edit Weekly Workout")

    day = st.selectbox("Select Day", list(workouts.keys()) or [today])

    muscle = st.text_input(
        "Muscle Group",
        workouts.get(day, {}).get("muscle_group", "")
    )

    exercises = workouts.get(day, {}).get("exercises", [])
    new_exercises = []

    st.subheader("Exercises")

    for i, ex in enumerate(exercises):
        cols = st.columns([4, 1, 1, 1])
        name = cols[0].text_input("Name", ex["name"], key=f"name_{i}")
        sets = cols[1].number_input("Sets", 1, 10, ex["sets"], key=f"sets_{i}")
        reps = cols[2].number_input("Reps", 1, 30, ex["reps"], key=f"reps_{i}")
        delete = cols[3].button("❌", key=f"del_{i}")

        if not delete:
            new_exercises.append({
                "name": name,
                "sets": sets,
                "reps": reps
            })

    if st.button("Add Exercise"):
        new_exercises.append({"name": "New Exercise", "sets": 3, "reps": 10})

    if st.button("Save Workout"):
        workouts[day] = {
            "muscle_group": muscle,
            "exercises": new_exercises
        }
        save_json(WORKOUT_FILE, workouts)
        st.success("Workout saved successfully.")

# -------------------------------------------------
# SETTINGS
# -------------------------------------------------
elif mode == "Settings":
    st.header("Settings")

    if st.button("Reset Today's Progress"):
        progress[today] = {}
        save_json(PROGRESS_FILE, progress)
        st.success("Today's progress reset.")

    if st.button("Reset Full Week"):
        progress.clear()
        save_json(PROGRESS_FILE, progress)
        st.success("Weekly progress reset.")
