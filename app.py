import pandas as pd
import streamlit as st

st.title("📊 Student Grade & Rewrite Tracker")

# --- CONNECT TO YOUR LIVE GOOGLE SHEET ---
SHEET_URL = (
   "https://docs.google.com/spreadsheets/d/16c-GKmXsPir279UyT71NinX30Hy-xH6ovjZeVo_yTZU/export?format=csv"
)


@st.cache_data(ttl=60)
def load_data(url):
  return pd.read_csv(url)


try:
  df = load_data(SHEET_URL)

  # --- 1. CLASS DROPDOWN ---
  st.header("1️⃣ Select Class")
  available_classes = sorted(df["Class"].dropna().unique().tolist())
  selected_class = st.selectbox("Choose a class:", available_classes)

  # Filter dataframe for selected class
  class_df = df[df["Class"] == selected_class]

  # --- 2. STUDENT DROPDOWN ---
  st.header("2️⃣ Select Student")
  class_df["DisplayName"] = (
      class_df["ChineseName"].astype(str)
      + " - "
      + class_df["EnglishName"].astype(str)
  )
  student_options = sorted(class_df["DisplayName"].tolist())
  selected_display_name = st.selectbox("Choose a student:", student_options)

  # --- 3. DISPLAY SCORES ---
  if selected_display_name:
    student_row = class_df[
        class_df["DisplayName"] == selected_display_name
    ].iloc[0]

    st.divider()
    st.subheader(f"Scores for: {student_row['DisplayName']}")
    st.write(f"**Student ID:** {student_row['StudentID']}")

    # Display a preview of a few columns if they exist
    cols = st.columns(3)
    if "Quiz_1" in student_row:
      cols[0].metric("Quiz 1", student_row["Quiz_1"])
    if "Hw_1" in student_row:
      cols[1].metric("Hw 1", student_row["Hw_1"])
    if "Hw_Average" in student_row:
      cols[2].metric("Hw Average", student_row["Hw_Average"])

except Exception as e:
  st.error(
      "Could not load data from Google Sheets. Please make sure your sheet is"
      " set to 'Anyone with the link can view'."
  )
  st.write(e)
