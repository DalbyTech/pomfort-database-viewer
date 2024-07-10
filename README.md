A basic Python tool for viewing the sqlite database of Pomfort Silverstack and Offload Manager apps in your web browser.


### Dependancies
```
pip install streamlit
pip install sqlite3
pip install pandas
```

### Usage
Edit the 'db_path' variable to point to your Silverstack / Offload Manager database.
eg:
```
db_path = "/Users/dalby/Library/Application Support/Pomfort/OffloadManager/Project-79C15709ECE3/OffloadManager.psdb"
```
or
```
db_path = "/Users/dalby/Library/Application Support/Pomfort/Silverstack/Project-79C15709ECE3/Silverstack8.psdb"
```

### Run the script:
```
streamlit run pomfort_db_explorer.py
```

You Mac should open a web browser window displaying the onctents of the database.
