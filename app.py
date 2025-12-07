import streamlit as st

st.title("Character Level Progress Calculator")

st.write("Enter current and target levels for each character.")

# ---- Character inputs ----
characters = ["Quinn", "Jabel", "Howard"]
results = {}

POINTS_PER_LEVEL = 100  # <-- change this if needed

for char in characters:
    st.subheader(char)
    current = st.number_input(f"Current level for {char}", min_value=0, value=0)
    target = st.number_input(f"Target level for {char}", min_value=current, value=current)

    levels_needed = target - current
    points_needed = levels_needed * POINTS_PER_LEVEL

    results[char] = (levels_needed, points_needed)

# ---- Display results ----
st.header("Results")

for char, (levels, points) in results.items():
    st.write(f"**{char}** needs **{levels} levels** more → **{points} points required**")

