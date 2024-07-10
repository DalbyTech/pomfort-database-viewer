import streamlit as st
import sqlite3
import pandas as pd
import pomfort

#Path to Pomfort Silverstack / Offload Manager Project Database:
db_path = "/Users/dalby/Library/Application Support/Pomfort/OffloadManager/Project-79C15709ECE3/OffloadManager.psdb"

st.set_page_config(
    layout='wide',
    page_title="DalbyTech: Pomfort Database Viewer"
)
st.title("DalbyTech: Pomfort Database Viewer", anchor=False)
st.divider()
with st.sidebar:
    with st.container(border=True):
        st.write("Database Path")
        st.caption(db_path)
    
    st.subheader("Tables", anchor=False)

conn = sqlite3.connect(db_path)
c = conn.cursor()

#Query to get all table names
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [table[0] for table in c.fetchall()]
tables.sort()


#Display data from every table:
for t in tables:

    title = pomfort.friendly_title(t)#filter sql table name and display an easier to read name

    main = st.container()


    with st.sidebar:


        if st.checkbox(title, key=t):

            with main:
                st.title(title)
                st.caption(t)

                #Query to select all data from the selected table
                c.execute(f"SELECT * FROM {t}")
                data = c.fetchall()

                #Fetch column names
                columns = [description[0] for description in c.description]

                #Create a DataFrame
                df = pd.DataFrame(data, columns=columns)

                #Display the DataFrame in Streamlit
                st.dataframe(df, use_container_width=True, height=500)
