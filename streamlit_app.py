import altair as alt
import pandas as pd
import streamlit as st

# Show the page title and description.
st.set_page_config(page_title="Movies dataset", page_icon="🎬")
st.title("🎬 Movies dataset")
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

# Show a multiselect widget with the genres using `st.multiselect`.
genres = st.multiselect(
    "Genres",
    df.genres.unique(),
    ["Action", "Adventure", "Biography", "Comedy", "Drama", "Horror"],
)

# Show a slider widget with the years using `st.slider`.
pages = st.slider("Length", 0, 2000, (0, 2000))

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[(df["genre"].isin(genres)) & (df["num_page"].between(pages[0], pages[1]))]
df_reshaped = df_filtered.pivot_table(
    index="pages", columns="genre", values="gross", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="pages", ascending=False)


# Display the data as a table using `st.dataframe`.
st.dataframe(
    df_reshaped,
    use_container_width=True,
    column_config={"pages": st.column_config.TextColumn("Pages")},
)

# Display the data as an  chart using 