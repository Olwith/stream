import streamlit as st
import pandas as pd
from io import StringIO

def main():
    st.title("Student Data Collection App")

    # Create placeholders for user input
    name = st.text_input("Enter Student Name:")
    age = st.number_input("Enter Student Age:", min_value=1, max_value=100, step=1)
    grade = st.selectbox("Select Grade Level:", ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5","Garde 6","Grade 7","Grade 8"])

    if 'student_data' not in st.session_state:
        st.session_state.student_data = pd.DataFrame(columns=["Name", "Age", "Grade"])

    if st.button("Submit"):
        # Create a dictionary to store the student data
        student_data = {
            "Name": name,
            "Age": age,
            "Grade": grade
        }

        # Convert the dictionary to a DataFrame
        new_data = pd.DataFrame([student_data])

        # Append new data to the session state DataFrame using pd.concat
        st.session_state.student_data = pd.concat([st.session_state.student_data, new_data], ignore_index=True)

        st.success("Data added successfully!")

    # Display the data in a table
    st.dataframe(st.session_state.student_data)

    # Provide an option to download the data as a CSV file
    if not st.session_state.student_data.empty:
        csv = st.session_state.student_data.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='student_data.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()
