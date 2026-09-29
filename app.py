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
  df.columns = df.columns.str.strip()
except Exception as e:
  st.error(f"Error loading data from Google Sheet: {e}")
  st.stop()


def find_column(dataframe, possible_names):
  for col in dataframe.columns:
    if col.lower() in [name.lower() for name in possible_names]:
      return col
  return None


id_col_name = find_column(df, ["StudentID", "Student ID", "ID"])
pin_col_name = find_column(df, ["PIN", "Pin", "Password"])

if not id_col_name or not pin_col_name:
  st.error(
      "Configuration Error: Could not find 'StudentID' or 'PIN' columns in"
      " your Google Sheet. Please check your column headers."
  )
  st.stop()

df[id_col_name] = df[id_col_name].astype(str).str.strip()
df[pin_col_name] = df[pin_col_name].astype(str).str.strip()


# --- LETTER GRADE HELPER FUNCTION ---
def get_letter_grade(score_val):
  try:
    score = float(score_val)
    if score >= 90:
      return "A+"
    elif score >= 80:
      return "A"
    elif score >= 75:
      return "B+"
    elif score >= 70:
      return "B"
    elif score >= 65:
      return "C+"
    elif score >= 60:
      return "C"
    else:
      return "D"
  except:
    return ""


# --- SIDEBAR QR CODE FOR STUDENTS ---
with st.sidebar:
  st.subheader("📱 Quick Login")
  st.write("Scan to open portal:")
  app_url = "https://science-grades-vth5uctmjxvsozrmdogwtk.streamlit.app/"
  qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={app_url}"
  st.image(qr_api_url, width=160)

  st.divider()
  st.markdown("### 📋 Grading Scale")
  st.markdown(
      """
    * **90 ~ 100** ➔ A+
    * **80 ~ 89** ➔ A
    * **75 ~ 79** ➔ B+
    * **70 ~ 74** ➔ B
    * **65 ~ 69** ➔ C+
    * **60 ~ 64** ➔ C
    * **0 ~ 59** ➔ D
    """
  )

st.title("🔬 Elementary Science Grade Portal")
st.markdown("Please log in with your Student ID and PIN to view your scores.")

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.student_id = ""

if not st.session_state.logged_in:
  with st.form("login_form"):
    st.subheader("Student Login")
    input_id = st.text_input("Student ID")
    input_pin = st.text_input("PIN", type="password")
    submit_button = st.form_submit_button("Log In")

    if submit_button:
      match = df[
          (df[id_col_name] == input_id.strip())
          & (df[pin_col_name] == input_pin.strip())
      ]

      if not match.empty:
        st.session_state.logged_in = True
        st.session_state.student_id = input_id.strip()
        st.rerun()
      else:
        st.error("Invalid Student ID or PIN. Please try again.")

else:
  student_data = df[df[id_col_name] == st.session_state.student_id]

  if not student_data.empty:
    student_row = student_data.iloc[0]

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
    st.write(f"**Student ID:** {student_row[id_col_name]}")
    if "Class" in student_row:
      st.write(f"**Class:** {student_row['Class']}")

    cols = st.columns(2)

    # --- SEPARATE GRADE 5 & GRADE 6 BOOKLET PAGE MAPPINGS ---
    HW_PAGES_G5 = {
        "Hw_1": "Pages 3",
        "Hw_2": "Pages 4",
        "Hw_3": "Pages 5",
        "Hw_4": "Pages 6",
        "Hw_5": "Pages 7 & 8",
        "Hw_6": "Pages 9 & 10",
        "Hw_7": "Pages 11 & 12",
        "Hw_8": "Pages 13",
        "Hw_9": "Pages 14",
    }

    HW_PAGES_G6 = {
        "Hw_1": "Pages 3 & 4",
        "Hw_2": "Pages 5 & 6",
        "Hw_3": "Pages 7 & 8",
        "Hw_4": "Pages 9 & 10",
        "Hw_5": "Pages 11 & 12",
    }

    # Automatically select the correct booklet based on student's class
    student_class = str(student_row.get("Class", ""))
    if "5" in student_class:
      active_hw_pages = HW_PAGES_G5
    else:
      active_hw_pages = HW_PAGES_G6

    # Hw 1 Display - Showing ONLY Letter Grade
    has_hw1 = False
    if "Hw_1" in student_row and student_row["Hw_1"] != "":
      hw1_val = student_row["Hw_1"]
      hw1_letter = get_letter_grade(hw1_val)
      cols[0].metric("Hw 1", hw1_letter if hw1_letter else "-")
      has_hw1 = True

    # Hw Average Display - Showing ONLY Letter Grade
    if "Hw_Average" in student_row and student_row["Hw_Average"] != "":
      hwa_val = student_row["Hw_Average"]
      hwa_letter = get_letter_grade(hwa_val)
      cols[1].metric("Hw Average", hwa_letter if hwa_letter else "-")

    # Dynamic Rewrite Prompt (Triggered at 90 and below, showing letter grade)
    if has_hw1:
      try:
        if float(student_row["Hw_1"]) <= 90:
          pages_to_do = active_hw_pages.get("Hw_1", "the assigned pages")
          st.info(
              f"💡 **Homework 1 Rewrite Opportunity:** Your current grade is"
              f" **{hw1_letter}**. Please complete your corrections for"
              f" **{pages_to_do}** in your booklet and average it with 100 to"
              " push your score higher!"
          )
      except:
        pass

    st.divider()

    st.markdown("### Detailed Scores & Homework Corrections")
    st.dataframe(student_data.drop(columns=[pin_col_name], errors="ignore"))

    if st.button("Log Out"):
      st.session_state.logged_in = False
      st.session_state.student_id = ""
      st.rerun()
  else:
    st.error("Account error. Please contact your teacher.")