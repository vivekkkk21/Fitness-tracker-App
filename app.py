import streamlit as st
import json
import os
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Workout Planner",
    layout="centered"
)

DATA_DIR = "."
WORKOUT_FILE = os.path.join(DATA_DIR, "workouts.json")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")

# -----------------------------
# UTILS
# -----------------------------
def load_json(path, default):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f, indent=4)
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# -----------------------------
# LOAD DATA
# -----------------------------
workouts = load_json(WORKOUT_FILE, {})
progress = load_json(PROGRESS_FILE, {})

today = datetime.now().strftime("%A")

if today not in progress:
    progress[today] = {}

# -----------------------------
# STYLES
# -----------------------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.card {
    background-color: #111827;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    border: 1px solid #1f2933;
}
.exercise {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.completed {
    text-decoration: line-through;
    opacity: 0.6;
}
.header {
    font-size: 36px;
    font-weight: 900;
}
.sub {
    font-size: 24px;
    color: #9ca3af;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------
mode = st.sidebar.radio("Mode", ["Today's Workout", "Edit Workout", "Settings"])

# -----------------------------
# TODAY VIEW
# -----------------------------
if mode == "Today's Workout":
    st.markdown(f"<div class='header'>{today}</div>", unsafe_allow_html=True)

    if today not in workouts:
        st.warning("No workout defined for today.")
    else:
        workout = workouts[today]
        st.markdown(f"<div class='sub'>{workout['muscle_group']}</div>", unsafe_allow_html=True)

        completed_count = 0

        for i, ex in enumerate(workout["exercises"]):
            key = f"{today}_{i}"
            done = progress[today].get(key, False)

            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                cols = st.columns([0.1, 0.9])
                checked = cols[0].checkbox("", value=done, key=key)

                if checked:
                    progress[today][key] = True
                    completed_count += 1
                    name_class = "completed"
                else:
                    progress[today][key] = False
                    name_class = ""

                cols[1].markdown(
                    f"<div class='{name_class}'><b>{ex['name']}</b> — "
                    f"{ex['sets']} × {ex['reps']}</div>",
                    unsafe_allow_html=True
                )

                st.markdown("</div>", unsafe_allow_html=True)

        save_json(PROGRESS_FILE, progress)
        st.progress(completed_count / len(workout["exercises"]))

# -----------------------------
# EDIT WORKOUT
# -----------------------------
elif mode == "Edit Workout":
    st.header("Edit Weekly Workout")

    day = st.selectbox("Select Day", list(workouts.keys()) or [today])

    muscle = st.text_input(
        "Muscle Group",
        workouts.get(day, {}).get("muscle_group", "")
    )

    exercises = workouts.get(day, {}).get("exercises", [])

    st.subheader("Exercises")

    new_exercises = []
    for i, ex in enumerate(exercises):
        cols = st.columns(4)
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

# -----------------------------
# SETTINGS
# -----------------------------
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
