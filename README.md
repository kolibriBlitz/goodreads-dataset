# 📚 Goodreads dataset app

## Navigation
- [code](https://github.com/kolibriBlitz/goodreads-dataset/tree/main/code): My kaggle notebooks, scraping script and Streamlit root code
- [data](https://github.com/kolibriBlitz/goodreads-dataset/tree/main/data): The dataset files
- [pages](https://github.com/kolibriBlitz/goodreads-dataset/tree/main/pages): Streamlit app code for subpages

## Project Goals
- Practice Python skills through hands-on, iterative querying.
- Think like a data analyst by looking for patterns, spotting anomalies, and turning data into actionable strategies.
- Build an app that allows users to search for book titles.

## Tech Stack
- Python: data import, data cleaning, data scraping and data analysis
- Streamlit: app development

## Methodology
1. Getting to know you: Studied the dataset using ```df.head(), df.describe(), df.dtypes```. Established a plan of attack to transform the data into a usable foundation for a booklist app.
2. Cleanliness is next to Godliness: Check data for anomalies and missing data to ensure accurate results.
3. *to be continued...*


## Results and Insights
- Collaborated with ChatGPT to write a data scraping script to locate missing page lengths.
- Goodreads data is surprisingly messy given the structured look of the website and app.
- Manga, comic books and independent authors had the greatest amount of missing data.
- Data is imbalanced toward fiction.
- *to be continued*

## Deliverables
A simple Streamlit app showing book data from [Goodreads](https://www.kaggle.com/datasets/). 

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://maven-goodreads-july2025.streamlit.app/)

- ### How to run it on your own machine

   1. Install the requirements

      ```
      $ pip install -r requirements.txt
      ```

   2. Run the app

      ```
      $ streamlit run streamlit_app.py
      ```
- ### Features
   - Side bar with three pages.
   - Home page with general search using filters and "find similar books" checkbox.
   - Visualizations page allowing users to explore the dataset and view my own favorites.
   - Random generator page where the user inputs a quantity of books and receives a random list for new reading adventures! 
