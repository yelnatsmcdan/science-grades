import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Science Student Grade Portal", page_icon="🔬", layout="centered"
)

SHEET_URL = "https://docs.google.com/spreadsheets/d/16c-GKmXsPir279UyT71NinX30Hy-xH6ovjZeVo_yTZU/export?format=csv"


@st.cache_data(ttl=60)
def load_data(url):
  return pd.read_csv(url)


try:
  df = load_data(SHEET_URL)
  # Clean column names
  df.columns = df.columns.str.strip()
except Exception as e:
  st.error(f"Error loading data from Google Sheet: {e}")
  st.stop()

st.title("🔬 Elementary Science Grade Portal")
st.markdown("Please log in with your Student ID and PIN to view your scores.")

# Initialize session state for login status
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.student_id = ""

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
  with st.form("login_form"):
    st.subheader("Student Login")
    input_id = st.text_input("Student ID")
    input_pin = st.text_input("PIN", type="password")
    submit_button = st.form_submit_button("Log In")

    if submit_button:
      # Ensure inputs and columns are strings for safe comparison
      df["StudentID"] = df["StudentID"].astype(str).str.strip()
      df["PIN"] = df["PIN"].astype(str).str.strip()

      match = df[
          (df["StudentID"] == input_id.strip())
          & (df["PIN"] == input_pin.strip())
      ]

      if not match.empty:
        st.session_state.logged_in = True
        st.session_state.student_id = input_id
        st.rerun()
      else:
        st.error("Invalid Student ID or PIN. Please try again.")

# --- SECURE DASHBOARD ---
else:
  student_data = df[df["StudentID"] == st.session_state.student_id]

  if not student_data.empty:
    student_row = student_data.iloc[0]

    # Combine Chinese and English names if they exist
    chinese_name = (
        str(student_row["ChineseName"])
        if "ChineseName" in student_row
        and pd.notna(student_row["ChineseName"])
        else ""
    )
    english_name = (
        str(student_row["EnglishName"])
        if "EnglishName" in student_row
        and pd.notna(student_row["EnglishName"])
        else ""
    )
    display_name = f"{chinese_name} - {english_name}".strip(" -")

    st.success(f"Welcome back, {display_name if display_name else 'Student'}!")

    st.subheader("Your Grade Report")
    st.write(f"**Student ID:** {student_row['StudentID']}")
    if "Class" in student_row:
      st.write(f"**Class:** {student_row['Class']}")

    # Display metric cards for quick viewing
    cols = st.columns(3)
    if "Quiz_1" in student_row:
      cols[0].metric("Quiz 1", student_row["Quiz_1"])
    if "Hw_1" in student_row:
      cols[1].metric("Hw 1", student_row["Hw_1"])
    if "Hw_Average" in student_row:
      cols[2].metric("Hw Average", student_row["Hw_Average"])

    st.divider()

    # Show full student record (hiding the PIN column for security)
    st.markdown("### Detailed Scores & Homework Corrections")
    st.dataframe(student_data.drop(columns=["PIN"], errors="ignore"))

    # Logout button
    if st.button("Log Out"):
      st.session_state.logged_in = False
      st.session_state.student_id = ""
      st.rerun()
  else:
    st.error("Account error. Please contact your teacher.")