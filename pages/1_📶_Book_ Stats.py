import streamlit as st
import pandas as pd
import numpy as py
import altair as alt

# Show the page title and description.
st.set_page_config(page_title="Book Stats", page_icon="📶")
st.markdown("# Goodreads Book Statistics")
st.sidebar.header("Book Stats")

st.markdown(
    "This page allows you to visualize correlations between book characteristics and ratings.")

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df1 = pd.read_csv("data/cleaned_works.csv",index_col='work_id')
    # df2 = pd.read_csv("data/goodreads_reviews.csv")
    return df1

df = load_data()
if st.checkbox("Show raw Data"):
    st.write(df)
    
# Do some light data cleaning
df["similar_books"] = df.similar_books.fillna('0')
df["similar_books"] = df.similar_books.str.split(', ').apply(
    lambda x: [int(n) for n in x] if x != ['0'] else [])
df["genres"] = df.genres.fillna('None')
df["genres"] = df.genres.str.split(', ').apply(
    lambda x: [n.strip() for n in x] if x != ['None'] else [])
df = df.explode("genres")
df = df.explode("similar_books")
df=df.drop(columns=["isbn","isbn13","image_url","description"])
df = df.rename(columns={'original_title': 'Title', 'author':'Author',
                'original_publication_year': 'Year',
               'num_pages': 'Length','genres':'Genre', '5_star_ratings': '5-Star', '4_star_ratings': '4-Star', '3_star_ratings': '3-Star', '2_star_ratings': '2-Star', '1_star_ratings': '1-Star'})
df=df.rename_axis('ID',axis="index")

# Bar Graphs
st.markdown("## 📊Bar Charts")
st.bar_chart(df, x='Length',y='Genre')

#Scatter Plots & Altair
st.markdown("## 🎲Scatter Plots")
st.scatter_chart(df,x='Length',y='avg_rating',color='avg_rating')

# Group and sort by average length
genre_length = df.groupby('Genre')['Length'].mean().reset_index()
genre_length = genre_length.sort_values('Length', ascending=False)

# Build the chart
bar = alt.Chart(genre_length).mark_bar().encode(
    x=alt.X('Length:Q', title='Average Book Length'),
    y=alt.Y('Genre:N', sort='-x', title='Genre'),
    color=alt.Color('Length:Q', scale=alt.Scale(scheme='darkmulti')),
    tooltip=['Genre', 'Length']
).properties(
    title='Average Book Length by Genre',
    width=700,
    height=500
)
color = alt.Color('Length:Q', scale=alt.Scale(scheme='reds'))


st.altair_chart(bar, use_container_width=True)

# Interactive Charts
st.markdown("## 🎮Interactive Graphs")

# Get user inputs
chart_type=st.radio('Choose your visual',['Bar','Scatter','Pivot Table'])
genre_list=st.multiselect('Choose a genre',df['Genre'].unique())
author_list=st.multiselect('Choose an author',df['Author'].sort_values(ascending=True))
length = st.slider('Filter by page length?',
                   df['Length'].min(), df['Length'].max(), (0, 2201))
rating=st.select_slider('Select a star rating',['1-Star','2-Star','3-Star','4-Star','5-Star'])

df_filtered = df[
    (df['Genre'].apply(lambda g_list: all(genre in g_list for genre in genre_list))) &
    (df['Author'].isin(author_list) if author_list else True) &
    (df['Length'].between(length[0], length[1])) & (df[rating])
]

if df_filtered.empty:
    st.warning("Nothing to see here. 👀")
else:
    if chart_type == 'Bar':
        st.markdown("### 📏 Average Book Length by Genre")
        genre_length = df_filtered.groupby(
            'Genre')['Length'].mean().reset_index()
        genre_length = genre_length.sort_values('Length', ascending=False)

        bar = alt.Chart(genre_length).mark_bar().encode(
            x=alt.X('Length:Q', title='Average Length (pages)'),
            y=alt.Y('Genre:N', sort='-x'),
            color=alt.Color('Length:Q', scale=alt.Scale(scheme='teals')),
            tooltip=['Genre', 'Length']
        ).properties(width=700, height=500)

        st.altair_chart(bar, use_container_width=True)

    elif chart_type == 'Scatter':
        st.markdown("### 📈 Book Length vs Average Rating")
        scatter = alt.Chart(df_filtered).mark_circle(size=60, opacity=0.6).encode(
            x=alt.X('Length:Q', title='Length (pages)'),
            y=alt.Y('avg_rating:Q', title='Average Rating'),
            color=alt.Color('Genre:N'),
            tooltip=['Title', 'Author', 'Genre', 'Length', 'avg_rating']
        ).interactive().properties(width=700, height=500)

        st.altair_chart(scatter, use_container_width=True)

    elif chart_type == 'Pivot Table':
        st.markdown("### ⭐ Average Star Ratings by Genre")
        pivot = df_filtered.groupby('Genre')[
            ['1-Star', '2-Star', '3-Star', '4-Star', '5-Star']].mean().reset_index()
        pivot_melted = pivot.melt(
            id_vars='Genre', var_name='Star Rating', value_name='Average Count')

        heatmap = alt.Chart(pivot_melted).mark_rect().encode(
            x=alt.X('Star Rating:N'),
            y=alt.Y('Genre:N'),
            color=alt.Color('Average Count:Q',
                            scale=alt.Scale(scheme='plasma')),
            tooltip=['Genre', 'Star Rating', 'Average Count']
        ).properties(width=700, height=500)

        st.altair_chart(heatmap, use_container_width=True)

    else:
        st.write("Ready Player 1 👾")





