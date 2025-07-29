st.markdown('### Similar Titles to Selections')
# Get titles from checked and add to a selectbox
books = checked.selection.rows
selected = df_filtered.iloc[books]['original_title'].to_list()
# title=st.selectbox("Selected Title", selected)


def run_similar():
    rows = st.session_state.get("selected_rows", [])
    if rows:
        titles = df_filtered.iloc[rows]["original_title"].tolist()
        st.session_state["selected_titles"] = titles
    else:
        st.session_state["selected_titles"] = []


# After rerun, show similar titles from session
if st.session_state.get("selected_titles"):

    for title in st.session_state["selected_titles"]:
        get_similar(title)
