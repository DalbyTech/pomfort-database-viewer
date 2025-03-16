import streamlit as st
import sqlite3
import pandas as pd
import pomfort
import datetime as dt
import os
import time

# Path to Pomfort Silverstack / Offload Manager Project Database:
db_path:str = None #set from within tab_settings

st.set_page_config(
    #layout="wide",
    page_title="DalbyTech: Pomfort Database Viewer"
)
st.title("DalbyTech: Pomfort Database Viewer")
st.divider()






def grab_table(table_name: str, col_order: list = None):
    col_order = col_order or []
    c.execute(f"SELECT * FROM {table_name}")
    data = c.fetchall()
    columns = [description[0] for description in c.description]
    df = pd.DataFrame(data, columns=columns)
    if col_order:
        col_order_set = set(col_order)
        remaining_cols = [col for col in columns if col not in col_order_set]
        df = df[col_order + remaining_cols]
    return df


class Job:
    def __init__(self, name):
        self.name = name
        self.progress = [None, None]   # [copy, verify]
        self.status = None
        self.added = None
        self.started = None
        self.completed = None
        self.priority = [None, None]   # [copy, verify]

    def update_from_row(self, row):
        """
        Update the job instance from a pandas Series row.
        Expects row to contain:
        ZNAME, ZPROGRESS, Z_ENT, ZCREATIONDATE, ZSTARTDATE, ZFINISHDATE, ZPRIORITY.
        """
        z_ent = row["Z_ENT"]
        idx = 0 if z_ent == 5 else 1 if z_ent == 9 else None

        if idx is not None:
            self.progress[idx] = float(row["ZPROGRESS"])
            self.priority[idx] = float(row["ZPRIORITY"])
            print('priority:', self.priority)


            if idx == 0 and self.progress[0] != 1.0 or idx == 1 and self.progress[0] == 1.0:
                self.status = pomfort.parse_ZSTATEIDENTIFIER(row["ZSTATEIDENTIFIER"])

            if  self.status is not None:
                status = self.status.lower()
                if   'unsuccessfull' in status: self.status = f'⚠️ {self.status}'
                elif 'successfull'   in status: self.status = f'✅ {self.status}'
            self.completed = row["ZFINISHDATE"]

    
def convert_date_values(df):
    df_copy = df.copy()
    date_columns = [col for col in df.columns if "DATE" in col and df[col].dtype == float]
    for col in date_columns:
        df_copy[col] = df_copy[col].apply(
            lambda x: pomfort.time.convert_pomfort_time(x) if pd.notnull(x) else x
        )
    return df_copy


cnt_status = st.container()

tab_jobs, tab_volumes, tab_all, tab_settings, = st.tabs(["Jobs", "Volumes", "All", "Settings"])

with tab_settings:
    with st.container(border=True):
        st.write("Select Database Path")
        db_path = st.selectbox("Pomfort Database Path", pomfort.database_paths)
        st.write(f'```{db_path}```')

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Query to get all table names
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = sorted([table[0] for table in c.fetchall()])


with tab_all:
    # Display data from every table (as before)
    main = st.container()
    with main:
        with st.expander("Tables"):
            for t in tables:
                title = pomfort.friendly_title(t)
                if st.checkbox(title, key=t):
                    with main:
                        df = grab_table(t)
                        st.subheader(title)
                        st.caption(t)
                        st.dataframe(df, use_container_width=True, height=500)

with tab_jobs:
    jobs_df = None
    jobs_dict = {}  # Dictionary of Job objects
    activity_table = None  # Name of the "Activity Job" table

    # Locate the "Activity Job" table and load its data.
    for t in tables:
        title = pomfort.friendly_title(t)
        if title == "Activity Job":
            activity_table = t
            jobs_df = grab_table(
                t, ["ZNAME", "ZPROGRESS", "Z_ENT", "ZCREATIONDATE", "ZSTARTDATE", "ZFINISHDATE", "ZPRIORITY"]
            )
            break

    from_date = st.number_input("Show Jobs From Last Days", min_value=1, value=1)

    if jobs_df is not None:
        # Convert date values
        jobs_df = convert_date_values(jobs_df)

        # Filter unfinished jobs (as in your original code)
        jobs_df = jobs_df[jobs_df["ZCREATIONDATE"] > pomfort.time.days_ago(from_date)]
        jobs_df.sort_values(by=["ZPRIORITY", "ZCREATIONDATE"], ascending=True, inplace=True)


        # Create or update Job objects from each row
        for _, row in jobs_df.iterrows():
            name = row["ZNAME"]
            #print (name, '>', pomfort.parse_ZSTATEIDENTIFIER(row["ZSTATEIDENTIFIER"]))
            if name not in jobs_dict:
                jobs_dict[name] = Job(name)          #add new job class to dict
            jobs_dict[name].update_from_row(row) #populate job class with data

        # Build a display DataFrame from the Job objects
        job_rows = []
        for job in jobs_dict.values():
            job_rows.append({
                "Job Name"       : job.name,
                "Copy Progress"  : int(job.progress[0]*100) if job.progress[0] is not None else 0,
                "Verify Progress": int(job.progress[1]*100) if job.progress[1] is not None else 0,
                "Priority"       : max(job.priority[0],job.priority[1]) if job.priority[0] is not None and job.priority[1] is not None else None,
                "Status"         : job.status,
            })

        df_jobs = pd.DataFrame(job_rows)
        df_jobs.sort_values(by=['Status', 'Priority', 'Copy Progress', 'Verify Progress'], ascending=[True, False, False, False], inplace=True, na_position='last')

        # Configure the progress columns so they render as progress bars.
        column_config = {
            "Job Name"       : st.column_config.Column        ("Job Name"       , disabled=True),
            "Copy Progress"  : st.column_config.ProgressColumn("Copy Progress"  , min_value=0, max_value=100, format="%.0f%%"),
            "Verify Progress": st.column_config.ProgressColumn("Verify Progress", min_value=0, max_value=100, format="%.0f%%"),
            "Priority"       : st.column_config.SelectboxColumn("Priority"      , options=([0,1,2,3,4,5]), width='small', help="Adjust Job Priority"),
            "Status"         : st.column_config.Column         ("Status"        , disabled=True),
        }

        #st.dataframe(df_jobs, column_config=column_config, use_container_width=True)
        edited_df_jobs = st.data_editor(df_jobs, column_config=column_config, use_container_width=True)

        # Check if any values in the "Priority" column have been changed
        error_count = 0
        for index, row in edited_df_jobs.iterrows():
            original_priority = df_jobs.at[index, "Priority"]
            new_priority = row["Priority"]

            if 'Unsuccessful' in str(row["Status"]):
                error_count +=1

            original_priority = float(original_priority) if original_priority is not None else 0.0
            if new_priority is not None:
                new_priority = float(new_priority)
            if original_priority is not None and new_priority is not None and float(original_priority) != float(new_priority):
                if float(original_priority) != float(new_priority):
                    c.execute(f"UPDATE {activity_table} SET ZPRIORITY = ? WHERE ZNAME = ?", (new_priority, row["Job Name"]))
                    conn.commit()
                    cnt_status.success(f"Updated priority for {row['Job Name']}")
                    # Ensure the priorities are the same kind of data


            print(f"Original Priority: {original_priority} (type: {type(original_priority)})")
            print(f"New Priority: {float(new_priority)} (type: {type(new_priority)})")

            if original_priority != new_priority:
                print("The priorities are different.")
            else:
                print("The priorities are the same.")


        if error_count > 0:
            cnt_status.error(f"{error_count} Unsuccessful Jobs", icon='⚠️')




with tab_volumes:
    # Locate the "Activity Job" table and load its data.
    show_offline = st.checkbox("Show Offline Volumes", value=False)

    volumes_df = None
    for t in tables:
        title = pomfort.friendly_title(t)
        if title == "Volume":
            activity_table = t
            volumes_df = grab_table(t, ["ZLABEL", "ZTOTALCAPACITY", "ZFREECAPACITY"])
            break
    
    volumes_df.sort_values(by=["ZISOFFLINE", "ZTOTALCAPACITY", "ZLABEL"], ascending=[True, False, True], inplace=True)

    # Filter volumes_df for values where ZISOFFLINE is False
    if not show_offline: volumes_df = volumes_df[(volumes_df["ZISOFFLINE"] == 0) & (volumes_df["ZTOTALCAPACITY"] > 0)]


    st.dataframe(volumes_df, use_container_width=True)  