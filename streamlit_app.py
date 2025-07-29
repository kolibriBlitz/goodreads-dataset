import altair as alt
import pandas as pd
import streamlit as st

# Show the page title and description.
st.set_page_config(page_title="Goodreads dataset", page_icon="📚")
st.title("📚 Goodreads dataset")
st.write(
    """
    This app visualizes data from [Goodreads](https://www.kaggle.com/datasets/melisandefritzsche/book-reviews).
    It shows thousands of books, their star ratings and other information. Just 
    click on the widgets below to explore!
    """
)


# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df1 = pd.read_csv("data/goodreads_works.csv")
    #df2 = pd.read_csv("data/goodreads_reviews.csv")
    return df1


df = load_data()

# Do some light data cleaning
df["num_pages"]=df.num_pages.fillna('0')
df["num_pages"]=df.num_pages.astype(int)

# Split genres string column into individual genres stored as a list
df['genres'] = df['genres'].str.split(',').apply(
    lambda lst: [genre.strip() for genre in lst])

# Show a multiselect widget with the genres using `st.multiselect`.
genres = st.multiselect("Genre", df['genres'].explode().unique(), ["fantasy","young-adult","romance"])


# Show a slider widget with the years using `st.slider`.
pages = st.slider("Length", df["num_pages"].min(),
                  df["num_pages"].max(),(0,2201),help="Number of pages")

# Show a slider with the number of stars
stars = st.slider("Rating",0.0,5.0,help="Average star rating")

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[
    df['genres'].apply(lambda g_list: any(genre in g_list for genre in genres)) &
    df['num_pages'].between(pages[0], pages[1]) & df['avg_rating'] >= stars
]

# possible reshape of dataframe



# Display the data as a table using `st.dataframe`.
st.dataframe(
    df_filtered,
    use_container_width=True, column_order=("original_title","author","num_pages","avg_rating"),
    column_config={"original_title": st.column_config.TextColumn("Title"), "author": st.column_config.TextColumn(
        "Author"), "num_pages": st.column_config.TextColumn("Length"), "avg_rating": st.column_config.TextColumn("Average Rating")},
)

# Display the data as an  chart using 