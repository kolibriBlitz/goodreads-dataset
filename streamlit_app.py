import pyarrow as pa
import altair as alt
import pandas as pd
import streamlit as st

# Show the page title and description.
st.set_page_config(page_title="Goodreads Book List", page_icon="📚")
st.title("📚 Goodreads Book List")
st.write(
    """
    This app visualizes data from [Goodreads](https://www.kaggle.com/datasets/melisandefritzsche/book-reviews).
    It shows thousands of books, their star ratings and other information. Just 
    click on the widgets below to explore!
    """
)

st.sidebar.header("Goodreads Dataset")
st.sidebar.success('Choose your adventure')

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df1 = pd.read_csv("data/goodreads_works.csv")
    # df2 = pd.read_csv("data/goodreads_reviews.csv")
    return df1


df = load_data()
if st.checkbox("Show raw Data"):
    st.write(df)
print(pa.__version__)
# Do some light data cleaning
df["num_pages"] = df.num_pages.fillna('0')
df["num_pages"] = df.num_pages.astype(int)
df["similar_books"] = df.similar_books.fillna('0')
df["similar_books"] = df.similar_books.str.split(', ').apply(
    lambda x: [int(n) for n in x] if x != ['0'] else [])

st.header("Filters")
left, right = st.columns(2)
# Split genres string column into individual genres stored as a list
df['genres'] = df['genres'].str.split(',').apply(
    lambda lst: [genre.strip() for genre in lst])

# Show a multiselect widget with the genres using `st.multiselect`.
genres = left.multiselect("Genre", df['genres'].explode().unique())

# Show a multiselect widget with the authors
authors = right.multiselect(
    "Author", df['author'].sort_values(ascending=True).unique())

# Show a slider widget with the years using `st.slider`.
pages = left.slider("Length", df["num_pages"].min(),
                    df["num_pages"].max(), (0, 2201), help="Number of pages")

# Show a slider widget with the number of stars
stars = right.slider("Rating", 0.0, 5.0, help="Average star rating")
# st.write(df['avg_rating'] >= stars)
# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[
    (df['genres'].apply(lambda g_list: all(genre in g_list for genre in genres))) & (df['author'].apply(lambda g_list: all(author in g_list for author in authors))) &
    (df['num_pages'].between(pages[0], pages[1])) & (df['avg_rating'] > stars)
]


# Function to show similar books to a selected title
def get_similar(title, df=df):
    '''Function accepts book title as string value. The cell in the dataframe containing the list of similar books for
    title is stored in a variable. 
    Function returns a dataframe containing information for similar books found.'''

    target = df.loc[df['original_title'].str.strip() == title]

    if target.empty:
        st.write(f"Sorry, {target['original_title'].iloc[0]} not found. 😔")
        return pd.DataFrame()  # or None, based on your preference

    # Extract the list of similar book IDs from the 'similar_books' column
    similar_list = target.iloc[0]['similar_books']

    # Check if similar_list is empty or null
    if not similar_list or (isinstance(similar_list, float) and pd.isna(similar_list)):
        st.write(f"😔 Sorry, there are no similar book suggestions for {target['original_title'].iloc[0]} from Goodreads.")
        st.markdown("---")
        return pd.DataFrame()

    # Filter df where work_id is in similar_list
    result = df.loc[df['work_id'].isin(similar_list)]
    
    # Display results all nice and pretty.
    st.write(
        f"🤓 Yay! Here are similar book suggestions for {target['original_title'].iloc[0]} from Goodreads.")
    st.dataframe(result, use_container_width=True, column_order=("original_title", "author", "num_pages", "avg_rating","genres"),
                 column_config={"original_title": st.column_config.TextColumn("Title"), "author": st.column_config.TextColumn(
                    "Author"), "num_pages": st.column_config.TextColumn("Length"), "avg_rating": st.column_config.TextColumn("Average Rating"),"genres":st.column_config.TextColumn("Genre")}, hide_index=True)
    st.markdown("---")


st.header("Book List 📖📕📙📗📘")


# Display the data as a table using `st.dataframe`. Include ability to get selctions for further manipulation.

checked = st.dataframe(
    df_filtered,
    use_container_width=True, column_order=("original_title", "author", "num_pages", "avg_rating"),
    column_config={"original_title": st.column_config.TextColumn("Title"), "author": st.column_config.TextColumn(
        "Author"), "num_pages": st.column_config.TextColumn("Length"), "avg_rating": st.column_config.TextColumn("Average Rating")}, hide_index=True, on_select="rerun", selection_mode="multi-row"
)
st.session_state.selected_rows = checked.selection.rows if checked.selection.rows else []

st.markdown('### Similar Titles to Selections')

# Only update session state when user clicks
if st.button("🔍 Find Similar Books"):
    selected_rows = checked.selection.rows
    st.session_state.selected_rows = selected_rows
    if selected_rows:
        titles = df_filtered.iloc[selected_rows]['original_title'].tolist()
        st.session_state.selected_titles = titles
    else:
        st.session_state.selected_titles = []

# Show similar books after button press
if st.session_state.get("selected_titles"):
    for title in st.session_state["selected_titles"]:
        get_similar(title)
