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
    df1 = pd.read_csv("data/cleaned_works.csv", index_col='work_id')
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
    reading_list = random.sample(range(0, 13525), k=(n))
    return reading_list

books = surprise_me(num_books)
temp = df.sort_values(by='total_reviews', ascending=False)

st.write("Surpise! Happy reading")
st.write({temp.iloc[books, lambda temp:[2,3,6,7]]})
