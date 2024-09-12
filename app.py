import itertools
import random
import time
import streamlit as st
import pandas as pd

# make streamlit auto width
st.set_page_config(layout="wide")

def generate_unique_data(numbers, n_samples, n_digits):
    # Menghasilkan semua kombinasi angka tanpa pengulangan dengan urutan berbeda
    all_combinations = list(itertools.permutations(numbers, n_digits))
    
    # Memastikan bahwa jumlah data yang diambil tidak melebihi jumlah kombinasi yang tersedia
    if n_samples > len(all_combinations):
        raise ValueError("Jumlah data melebihi jumlah kombinasi yang mungkin.")
    
    # Mengacak kombinasi dan memilih n_samples data secara unik
    random.shuffle(all_combinations)
    unique_data = all_combinations[:n_samples]
    
    # Buat list untuk menyimpan angka yang tidak ada di kombinasi
    missing_numbers = []
    
    # Untuk setiap kombinasi, temukan angka yang tidak ada di dalamnya
    for comb in unique_data:
        missing_number = [num for num in numbers if num not in comb][0]
        missing_numbers.append(missing_number)
    
    # Mengubah setiap kombinasi menjadi string
    unique_data_str = [''.join(map(str, comb)) for comb in unique_data]
    
    return unique_data_str, missing_numbers

# Function to format the elapsed time
def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes} minute(s) {seconds} second(s)"

# Function to check whether each generated number matches the corresponding missing number
def check_match(generated_numbers, missing_numbers):
    match_state = [int(gen) == int(miss) for gen, miss in zip(generated_numbers, missing_numbers)]
    return match_state

st.header("Computer Assisted Test (CAT) Simulation")
st.markdown("-----")
panels = st.columns(2)

with panels[0]:
    st.text("Input 5 numbers (must be unique)")

    # Input 5 angka
    five_columns = st.columns(5)

    number_1 = five_columns[0].number_input("Number 1", min_value=0, max_value=9)
    number_2 = five_columns[1].number_input("Number 2", min_value=0, max_value=9)
    number_3 = five_columns[2].number_input("Number 3", min_value=0, max_value=9)
    number_4 = five_columns[3].number_input("Number 4", min_value=0, max_value=9)
    number_5 = five_columns[4].number_input("Number 5", min_value=0, max_value=9)

    generate_button = st.button("Generate Random Numbers", use_container_width=True)

    # Initialize session state for result, missing_numbers, start_time, and elapsed_time
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'missing_numbers' not in st.session_state:
        st.session_state.missing_numbers = None
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'elapsed_time' not in st.session_state:
        st.session_state.elapsed_time = None
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    # Start timer when the generate button is clicked
    if generate_button:
        numbers = [number_1, number_2, number_3, number_4, number_5]
        n_samples = 35
        n_digits = 4
        st.session_state.result, st.session_state.missing_numbers = generate_unique_data(numbers, n_samples, n_digits)
        st.session_state.start_time = time.time()  # Start the timer
        st.session_state.submitted = False  # Reset submitted state when generating new data

    # Display the DataFrame if the result is available
    if st.session_state.result is not None:
        df = pd.DataFrame({'Generated Numbers': st.session_state.result, 'Missing Numbers': [""] * 35})
        edited_df = st.data_editor(df, use_container_width=True)

        # Update session state with any edits made to the DataFrame
        st.session_state.result = edited_df['Generated Numbers'].tolist()

        # Add a "Submit" button
        submit_button = st.button("Submit", use_container_width=True)

        # Stop the timer when the submit button is clicked

        with panels[1]:
            if submit_button:
                # st.subheader("Results")
                st.session_state.submitted = True
                total_time = time.time() - st.session_state.start_time
                st.info(f"Total time: {format_time(total_time)}")
            
            details_1 = st.columns(2)
            details_2 = st.columns(2)

            # Display the final DataFrame after submission
            if st.session_state.submitted:
                # st.write("Final Submitted Data:")
                final_df = edited_df
                final_df["Your Answer"] = final_df["Missing Numbers"].tolist()
                final_df["Missing Numbers"] = st.session_state.missing_numbers
                match_state = check_match(final_df["Missing Numbers"].tolist(), final_df["Your Answer"].tolist())
                final_df["Matched"] = match_state
                st.dataframe(final_df, use_container_width=True)
            
                # Count the number of True and False matches
                true_count = sum(match_state)
                false_count = len(match_state) - true_count
                true_percentage = (true_count / len(match_state)) * 100
                false_percentage = (false_count / len(match_state)) * 100

                # Display the counts and percentages
                details_1[0].success(f"True: {true_count}")
                details_1[1].error(f"False: {false_count}")
                details_2[0].success(f"True: {true_percentage:.2f}%")
                details_2[1].error(f"False: {false_percentage:.2f}%")
                # details_2.info(f"True: {true_percentage:.2f}%, False: {false_percentage:.2f}%")
