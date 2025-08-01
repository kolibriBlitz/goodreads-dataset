import streamlit as st
import pandas as pd
import random

st.set_page_config('Feeling Lucky?', '🍀')

st.title('Surprise Me!')
st.markdown('## Random Reading List Generator')
st.sidebar.header("Feeling Lucky")

st.markdown(
    "This page allows you get a random assortment of books.")

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).


@st.cache_data
def load_data():
    df1 = pd.read_csv("data/cleaned_works.csv")
    # df2 = pd.read_csv("data/goodreads_reviews.csv")
    return df1


df = load_data()
book_list = df
# Define random selection function


def surprise_me(n):
    '''
    Function expects integer value for book list amount.
    Returns a random sample of k amount from dataframe rows range. List is meant to be used to locate rows in full book_list dataframe.
    '''
    book_ids = random.sample(range(0, 13525), k=(n))
    return book_ids


# Initialize session state
if "book_list" not in st.session_state:
    st.session_state.book_list = []

# Get user input
num_books = st.number_input('How many books do you want to read?', 0, 13525,)
st.markdown('---')

# Run function and filter data
if st.button('Surprise me! 🙈'):
    st.session_state.book_list = surprise_me(num_books)

filtered_df = df.loc[st.session_state.book_list]

# Display results
if st.session_state.book_list:
    st.write("Surpise! 🥳 Happy reading")
    st.dataframe(
        filtered_df,
        use_container_width=True, column_order=("Title", "author", "num_pages", "avg_rating"),
        column_config={"author": st.column_config.TextColumn(
            "Author"), "num_pages": st.column_config.TextColumn("Length"), "avg_rating": st.column_config.TextColumn("Average Rating")}, hide_index=True
    )
